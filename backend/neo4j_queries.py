from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import sys
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
URI = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(user, password))

def get_answer_neo4j(question):
    contexts = []
    chunkIds = []
    scores = []

    with driver.session() as session:

        query = """
            SHOW INDEXES YIELD name, type, state
            WHERE type = 'VECTOR'
        """

        result = session.run(query)
        for record in result:
            print(f"Index: {record['name']}, State: {record['state']}")

        query = """        
            WITH genai.vector.encode(
                $question, 
                "OpenAI", 
                {
                token: $openAiApiKey
                }) AS question_embedding
            CALL db.index.vector.queryNodes(
                "chunk_content_embeddings", 
                $top_k, 
                question_embedding
                ) YIELD node AS chunk, score
            RETURN chunk.name, chunk.content, score
        """
        result = session.run(
            query, {"question": question, "openAiApiKey": OPENAI_API_KEY, "top_k": 5}
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
    {name: n.name, properties: apoc.map.fromLists(keys(n), [p in keys(n) | n[p]])} AS node,
    collect({
          neighbor: {name: neighbor.name, properties: apoc.map.fromLists(keys(neighbor), [p in keys(neighbor) | neighbor[p]])},
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


