from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import sys
import openai
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import time
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
URI = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(user, password))

def get_response(user_query, contexts, chat_history):
    template = """
    You are a helpful assistant. Answer the following questions considering the history of the conversation:

    Chat history: {chat_history}

    Contexts: {contexts}

    User question: {user_question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI()

    chain = prompt | llm | StrOutputParser()

    return chain.invoke(
        {
            "chat_history": chat_history,
            "contexts": contexts,
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
            query_1, parameters={"question_embedding": question_embedding, "top_k": 5}
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
            WITH c, count(distinct n) AS freq, nodes  // Include 'nodes' here
            ORDER BY freq DESC
            LIMIT $topChunks
            WITH collect(elementId(c)) AS chunk_ids, nodes  // Collect only IDs

            // Entity - Report Mapping
            UNWIND nodes AS n
            MATCH (n)-[:IN_COMMUNITY]->(c:__Community__)
            WITH c, c.community_rank AS rank, chunk_ids  // Include 'chunk_ids' here
            ORDER BY rank DESC
            LIMIT $topCommunities
            WITH chunk_ids, collect(elementId(c)) AS community_ids  // Collect only IDs

            RETURN {Chunks: chunk_ids, Reports: community_ids} AS ids
        """
        local_retriever_result = session.run(
                query_2, {"node_ids": entity_ids, "topChunks": 5, "topCommunities": 5}
            )
        print("After second query", file=sys.stdout)
        data_list = []
        for record in local_retriever_result:
            text_mapping = record["ids"]["Chunks"]
            report_mapping = record["ids"]["Reports"]

            # Create a dictionary to store the collected information
            data = {
                "text_mapping": text_mapping,
                "report_mapping": report_mapping,
            }
            
            # Append to the list
            data_list.append(data)

    return data_list[0]


def global_retriever(question):
    community_ids = []

    question_embedding = encode_question(question)
    with driver.session() as session:
        query = """        
            WITH $question_embedding AS question_embedding
            CALL db.index.vector.queryNodes(
                "community_embeddings", 
                $top_k, 
                question_embedding
                ) YIELD node AS community, score
            RETURN elementId(community) AS community_id
        """
        result = session.run(query, parameters={"question_embedding": question_embedding, "top_k": 5})
        for record in result:
            id = record["community_id"]
            community_ids.append(id)
    return community_ids

def get_aux_entity_nodes(local_text_chunk_ids, local_summary_ids, global_summary_ids):
    query_1 = """
        WITH $local_text_chunk_ids AS local_text_chunk_ids, 
            $local_summary_ids AS local_summary_ids, 
            $global_summary_ids AS global_summary_ids

        MATCH (e:__Entity__)-[r]->(n)
        WHERE elementId(n) IN local_text_chunk_ids OR elementId(n) IN local_summary_ids OR elementId(n) IN global_summary_ids
        WITH e, COUNT(DISTINCT n) AS connections
        WHERE connections >= 2
        RETURN elementId(e) as entity_id
        LIMIT 10
    """
    with driver.session() as session:
        result = session.run(query_1, {
            "local_text_chunk_ids": local_text_chunk_ids,
            "local_summary_ids": local_summary_ids,
            "global_summary_ids": global_summary_ids
        })
        entity_nodes = [record["entity_id"] for record in result]

    return entity_nodes

def get_subgraph(question):
    local_report = local_retriever(question)
    local_text_chunk_ids = local_report["text_mapping"]
    local_summary_ids = local_report["report_mapping"]
    global_summary_ids = global_retriever(question)

    entity_nodes = get_aux_entity_nodes(local_text_chunk_ids, local_summary_ids, global_summary_ids)    
    
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
                            type: type(r)}) AS edges

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

    return {"nodes": nodes, "edges": edges}


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

def query_subgraph(chunkIds):
    query = """
    WITH $chunkIds AS names
    MATCH (n)
    WHERE n.name IN names
    OPTIONAL MATCH (n)-[r]-(neighbor)
    RETURN 
    {name: n.name, labels: labels(n), properties: apoc.map.fromLists(keys(n), [p in keys(n) | n[p]])} AS node,
    collect({
          neighbor: {name: neighbor.name, labels: labels(neighbor), properties: apoc.map.fromLists(keys(neighbor), [p in keys(neighbor) | neighbor[p]])},
          relationship: {label: type(r), properties: apoc.map.fromLists(keys(r), [p in keys(r) | r[p]])}
    }) AS neighbors
    """

    records = []
    with driver.session() as session:
        for record in session.run(query, {"chunkIds": chunkIds}):
            records.append(record)

    return records

def query_secondary_nodes(primaryNodes):
    query = """
    UNWIND $primaryNodes AS primaryNode
    MATCH (n)
    WHERE n.name = primaryNode
    OPTIONAL MATCH (n)-[r]-(neighbor)
    WHERE NOT neighbor:__Chunk__
    WITH neighbor, neighbor.name AS secondaryNode, count(DISTINCT n.name) AS primaryCount
    WHERE primaryCount >= 2
    RETURN
    secondaryNode AS name, apoc.map.fromLists(keys(neighbor), [p in keys(neighbor) | neighbor[p]]) AS properties
    """

    secondary_nodes = []
    with driver.session() as session:
        for record in session.run(query, {"primaryNodes": primaryNodes}):
            secondary_nodes.append(record["name"])
    return secondary_nodes

def query_appeared_in_nodes(secondaryNodes):
    query = """
    UNWIND $secondaryNodes AS secondaryNode
    MATCH (s {name: secondaryNode})
    OPTIONAL MATCH (s)-[r:APPEARED_IN]->(appearedInNode)
    RETURN
    s.name AS secondaryNodeName,
    collect({
        name: appearedInNode.name,
        properties: apoc.map.fromLists(keys(appearedInNode), [p in keys(appearedInNode) | appearedInNode[p]])
    }) AS appearedInNodes
    """

    appeared_in_nodes = {}
    with driver.session() as session:
        for record in session.run(query, {"secondaryNodes": secondaryNodes}):
            appeared_in_nodes.update({
                record["secondaryNodeName"]: record["appearedInNodes"]
            })
    return appeared_in_nodes


            # WITH genai.vector.encode(
            #     $question, 
            #     "OpenAI", 
            #     {
            #     token: $openAiApiKey
            #     }) AS question_embedding