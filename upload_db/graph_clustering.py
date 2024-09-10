import json
import os
import time
from pathlib import Path
# from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_community.graphs import Neo4jGraph
from graphdatascience import GraphDataScience
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore
from tqdm import tqdm

# Load environment variables
def load_env():
    """Load environment variables from .env file."""
    # load_dotenv()
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "NEO4J_URI": os.getenv("NEO4J_URI"),
        "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME"),
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD")
    }

# Initialize Neo4j Graph and Graph Data Science instance
def init_graph(env_vars):
    """Initialize Neo4j Graph and Graph Data Science instance."""
    graph = Neo4jGraph(refresh_schema=False)
    gds = GraphDataScience(
        env_vars["NEO4J_URI"],
        auth=(env_vars["NEO4J_USERNAME"], env_vars["NEO4J_PASSWORD"])
    )
    return graph, gds

# Create or retrieve graph projection
def setup_graph_projection(gds, graph_name="communities"):
    # """Create or retrieve graph projection."""
    # graph_exists, _ = gds.graph.exists(graph_name)
    # if graph_exists:
    #     G = gds.graph.get(graph_name)
    # else:
        G, _ = gds.graph.project(
            graph_name,
            "__Entity__",
            {
                "_ALL_": {
                    "type": "*",
                    "orientation": "UNDIRECTED",
                    "properties": {"weight": {"property": "*", "aggregation": "COUNT"}},
                }
            },
        )
        return G

# Perform community detection and write results to the graph
def detect_communities(gds, G):
    """Perform community detection using the Leiden algorithm."""
    wcc = gds.wcc.stats(G)  # Optionally use the result if needed
    gds.leiden.write(
        G,
        writeProperty="communities",
        includeIntermediateCommunities=True,
        relationshipWeightProperty="weight",
    )

# Update community relationships and ranks
def update_community_relationships(graph):
    """Update community relationships and calculate ranks in the graph."""
    graph.query("""
    MATCH (e:`__Entity__`)
    UNWIND range(0, size(e.communities) - 1 , 1) AS index
    CALL {
        WITH e, index
        WITH e, index
        WHERE index = 0
        MERGE (c:`__Community__` {id: toString(index) + '-' + toString(e.communities[index])})
        ON CREATE SET c.level = index
        MERGE (e)-[:IN_COMMUNITY]->(c)
        RETURN count(*) AS count_0
    }
    CALL {
        WITH e, index
        WITH e, index
        WHERE index > 0
        MERGE (current:`__Community__` {id: toString(index) + '-' + toString(e.communities[index])})
        ON CREATE SET current.level = index
        MERGE (previous:`__Community__` {id: toString(index - 1) + '-' + toString(e.communities[index - 1])})
        ON CREATE SET previous.level = index - 1
        MERGE (previous)-[:IN_COMMUNITY]->(current)
        RETURN count(*) AS count_1
    }
    RETURN count(*)
    """)

    graph.query("""
    MATCH (c:__Community__)<-[:IN_COMMUNITY*]-(:__Entity__)-[:APPEARED_IN]->(d:__Chunk__)
    WITH c, count(distinct d) AS rank
    SET c.community_rank = rank;
    """)

# Prepare data for generating community summaries
def fetch_community_info(graph):
    """Fetch community information for generating summaries."""
    return graph.query("""
    MATCH (c:`__Community__`)<-[:IN_COMMUNITY*]-(e:__Entity__)
    WHERE c.level IN [0]
    WITH c, collect(e ) AS nodes
    WHERE size(nodes) > 1
    CALL apoc.path.subgraphAll(nodes[0], {
        whitelistNodes:nodes
    })
    YIELD relationships
    RETURN c.id AS communityId,
           [n in nodes | {id: n.id, description: n.description, type: [el in labels(n) WHERE el <> '__Entity__'][0]}] AS nodes,
           [r in relationships | {start: startNode(r).id, type: type(r), end: endNode(r).id, description: r.description}] AS rels
    """)

# Prepare a string for OpenAI API
def prepare_string(data):
    """Prepare string representation of nodes and relationships for input to LLM."""
    nodes_str = "Nodes are:\n"
    for node in data['nodes']:
        node_id = node['id']
        node_type = node['type']
        node_description = f", description: {node['description']}" if 'description' in node and node['description'] else ""
        nodes_str += f"id: {node_id}, type: {node_type}{node_description}\n"

    rels_str = "Relationships are:\n"
    for rel in data['rels']:
        start = rel['start']
        end = rel['end']
        rel_type = rel['type']
        description = f", description: {rel['description']}" if 'description' in rel and rel['description'] else ""
        rels_str += f"({start})-[:{rel_type}]->({end}){description}\n"

    return nodes_str + "\n" + rels_str

# Generate summaries using OpenAI API
def generate_summary(data, community_chain):
    """Generate natural language summary using OpenAI API."""
    stringify_info = prepare_string(data)
    summary = community_chain.invoke({'community_info': stringify_info})
    return {"community": data['communityId'], "summary": summary}

# Configure LLM and prompt
def configure_llm():
    """Configure language model and prompt template."""
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini-2024-07-18")
    community_template = """Based on the provided nodes and relationships that belong to the same graph community,
    generate a natural language summary of the provided information:
    {community_info}

    Summary:"""
    community_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Given an input triples, generate the information summary. No pre-amble."),
            ("human", community_template),
        ]
    )
    community_chain = community_prompt | llm | StrOutputParser()
    return community_chain

# Process communities with throttling
def process_communities_with_throttle(community_info, community_chain, max_concurrent_requests=5, delay_between_requests=0.5):
    """Process communities to generate summaries with throttling."""
    semaphore = Semaphore(max_concurrent_requests)
    summaries = []

    def process_community(community):
        with semaphore:
            result = generate_summary(community, community_chain)
            time.sleep(delay_between_requests)
            return result

    with ThreadPoolExecutor(max_workers=max_concurrent_requests) as executor:
        futures = {executor.submit(process_community, community): community for community in community_info}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing communities"):
            summaries.append(future.result())

    return summaries

# Update graph with community summaries
def update_community_summaries(graph, summaries):
    """Update graph database with generated community summaries."""
    graph.query("""
    UNWIND $data AS row
    MERGE (c:__Community__ {id:row.community})
    SET c.summary = row.summary
    """, params={"data": summaries})

# Main function to execute the entire process
def main():
    # Load environment variables and configure
    env_vars = load_env()

    # Initialize graph and GDS instances
    graph, gds = init_graph(env_vars)

    # Setup or retrieve graph projection
    G = setup_graph_projection(gds)

    # Detect communities and update relationships
    detect_communities(gds, G)
    update_community_relationships(graph)

    # Fetch community info
    community_info = fetch_community_info(graph)

    # Configure LLM
    community_chain = configure_llm()

    # Process communities and generate summaries
    summaries = process_communities_with_throttle(community_info, community_chain)

    # Update graph with generated summaries
    update_community_summaries(graph, summaries)

if __name__ == "__main__":
    main()
