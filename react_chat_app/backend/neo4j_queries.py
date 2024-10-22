from neo4j import GraphDatabase
import os

import sys
import openai
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import time


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
URI = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(user, password))

def get_response(user_query, contents, summaries, chat_history):
    template = """
    You are a helpful assistant. Answer the following questions considering the history of the conversation:

    Chat history: {chat_history}

    Contents: {contents}

    Summaries: {summaries}

    User question: {user_question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI()

    chain = prompt | llm | StrOutputParser()

    return chain.invoke(
        {
            "chat_history": chat_history,
            "contents": contents,
            "summaries": summaries,
            "user_question": user_query,
        }
    )


def encode_question(question):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    retry_attempts = 5
    for attempt in range(retry_attempts):
        try:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=question
            )
            return response.data[0].embedding
        except client.RateLimitError as e:
            if attempt < retry_attempts - 1:
                time.sleep(2 * attempt)
            else:
                raise e

def local_retriever(question):
    entity_ids = []
    question_embedding = encode_question(question)
    contexts = {}
    with driver.session() as session:

        query_1 = """        
            WITH $question_embedding AS question_embedding
            CALL db.index.vector.queryNodes(
                "entity_embeddings", 
                $top_k, 
                question_embedding
                ) YIELD node AS entity
            RETURN elementId(entity) AS entity_id
        """
        nodes_result = session.run(
            query_1, parameters={"question_embedding": question_embedding, "top_k": 10}
        )
        print("After first query", file=sys.stdout)
        for record in nodes_result:
            entity_ids.append(record["entity_id"])

        query_2 = """
            WITH $node_ids AS node_ids
            MATCH (n)
            WHERE elementId(n) IN node_ids
            WITH collect(n) AS nodes

            // Entity - Text Unit Mapping
            UNWIND nodes AS n
            MATCH (n)-[:APPEARED_IN]->(c:__Chunk__)
            WITH c, c.content AS content, count(distinct n) AS freq, nodes  // Include 'c.content' here
            ORDER BY freq DESC
            LIMIT $topChunks
            WITH collect(elementId(c)) AS chunk_ids, collect(content) AS chunk_contents, nodes  // Collect 'content' and 'chunk_ids'

            // Entity - Report Mapping
            UNWIND nodes AS n
            MATCH (n)-[:IN_COMMUNITY]->(c:__Community__)
            WITH c, c.community_rank AS rank, chunk_ids, chunk_contents, c.summary AS summary  // Include 'c.summary' here
            ORDER BY rank DESC
            LIMIT $topCommunities
            WITH chunk_ids, chunk_contents, collect(elementId(c)) AS community_ids, collect(summary) AS community_summaries  // Collect 'summary' and 'community_ids'

            // Return the results with contents and summaries
            RETURN {Chunks: chunk_ids, ChunkContents: chunk_contents, Reports: community_ids, CommunitySummaries: community_summaries} AS ids
        """
        local_retriever_result = session.run(
                query_2, {"node_ids": entity_ids, "topChunks": 5, "topCommunities": 5}
            )
        print("After second query", file=sys.stdout)
        data_list = []
        for record in local_retriever_result:
            text_mapping = record["ids"]["Chunks"]
            report_mapping = record["ids"]["Reports"]
            contents = record["ids"]["ChunkContents"]
            summaries = record["ids"]["CommunitySummaries"]

            # Create a dictionary to store the collected information
            data = {
                "text_mapping": text_mapping,
                "report_mapping": report_mapping,
                "contents": contents,
                "summaries":summaries
            }
            
            # Append to the list
            data_list.append(data)


    return data_list[0], entity_ids


def global_retriever(question):
    community_ids = []
    summaries = []
    question_embedding = encode_question(question)
    with driver.session() as session:
        query = """        
            WITH $question_embedding AS question_embedding
            CALL db.index.vector.queryNodes(
                "community_embeddings", 
                $top_k, 
                question_embedding
                ) YIELD node AS community, score
            RETURN elementId(community) AS community_id, community.summary as summary
        """
        result = session.run(query, parameters={"question_embedding": question_embedding, "top_k": 5})
        for record in result:
            id = record["community_id"]
            summary = record["summary"]
            community_ids.append(id)
            summaries.append(summary)
    return community_ids, summaries

def get_subgraph(question):
    local_report, entity_nodes = local_retriever(question)
    local_text_chunk_ids = local_report["text_mapping"]
    local_summary_ids = local_report["report_mapping"]
    local_contents = local_report["contents"]
    local_summaries = local_report["summaries"]
    global_summary_ids, global_summaries = global_retriever(question)
    summaries = global_summaries + local_summaries
    print("In the get_subgraph", file=sys.stdout)
    print(summaries, file=sys.stdout)
    print(local_summaries, file=sys.stdout)
    print(local_contents, file=sys.stdout)
    query_2 = """
        WITH $local_text_chunk_ids AS local_text_chunk_ids, 
             $local_summary_ids AS local_summary_ids, 
             $global_summary_ids AS global_summary_ids,
             $entity_ids AS entity_ids

        MATCH (n)-[r]-(m)
        WHERE (elementId(n) IN local_text_chunk_ids 
               OR elementId(n) IN local_summary_ids 
               OR elementId(n) IN global_summary_ids
               OR elementId(n) IN entity_ids) 
              AND (elementId(m) IN local_text_chunk_ids 
                   OR elementId(m) IN local_summary_ids 
                   OR elementId(m) IN global_summary_ids 
                   OR elementId(m) IN entity_ids)
        // Collect all node properties including IDs
        WITH collect(DISTINCT {id: elementId(n), type: labels(n), properties: properties(n)}) AS nodes,  
            collect(DISTINCT {from: elementId(startNode(r)), 
                            to: elementId(endNode(r)), 
                            label: type(r)}) AS edges

        RETURN nodes, edges;
        
    """
    with driver.session() as session:
        result = session.run(query_2, {
            "local_text_chunk_ids": local_text_chunk_ids,
            "local_summary_ids": local_summary_ids,
            "global_summary_ids": global_summary_ids,
            "entity_ids": entity_nodes
        })
        for record in result:
            nodes = record['nodes']
            for node in nodes:
                node_dict = dict(node)
                node_dict["properties"].pop("entityEmbedding", None)
                node_dict["properties"].pop("communityEmbedding", None)
                node_dict["properties"].pop("contentEmbedding", None)
                print(node_dict, file=sys.stdout)
            
            edges = record['edges']

            # print(f"{type(record['edges'])} and length {len(record['edges'])}", file=sys.stdout)

    return {"nodes": nodes, "edges": edges}, {"contents": local_contents, "summaries": summaries}


def get_answer_neo4j(question):
    contexts = []
    chunkIds = []
    scores = []
    question_embedding = encode_question(question)
    with driver.session() as session:
        query = """        
            WITH $question_embedding AS question_embedding
            CALL db.index.vector.queryNodes(
                "chunk_content_embeddings", 
                $top_k, 
                question_embedding
                ) YIELD node AS chunk, score
            RETURN chunk.name, chunk.content, score
        """
        result = session.run(
            query, {"question_embedding": question_embedding, "openAiApiKey": OPENAI_API_KEY, "top_k": 5}
            # query, {"question": question, "openAiApiKey": OPENAI_API_KEY}
        )
        for record in result:
            name = record["chunk.name"]
            scores.append(record["score"])
            chunkIds.append(name)
            contexts.append(record["chunk.content"])

    return contexts, chunkIds, scores

