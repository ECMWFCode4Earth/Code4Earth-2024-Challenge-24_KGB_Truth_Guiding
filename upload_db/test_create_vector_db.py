from neo4j import GraphDatabase
import openai
import os

# Set up OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Neo4j configuration
URI = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(user, password))

def encode_text(text):
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def update_neo4j_with_embeddings():
    with driver.session() as session:
        try:
            result = session.run("MATCH (n:Chunk) WHERE n.content IS NOT NULL RETURN n.content, ID(n) AS id")
            for record in result:
                content = record["n.content"]
                node_id = record["id"]
                
                if not content:
                    print(f"Skipping empty content for node ID {node_id}")
                    continue
                
                try:
                    embedding = encode_text(content)
                except Exception as e:
                    print(f"Error getting embedding for node ID {node_id}: {e}")
                    continue
                
                if embedding:
                    session.run(
                        "MATCH (n:Chunk) WHERE ID(n) = $id SET n.contentEmbedding = $embedding",
                        id=node_id, embedding=embedding
                    )
                    print(f"Set embedding for node ID {node_id}")
                else:
                    print(f"No embedding returned for node ID {node_id}")
        except Exception as e:
            print("An error occurred:", e)

def verify_embeddings():
    with driver.session() as session:
        try:
            result = session.run(
                """
                MATCH (m:Chunk)
                WHERE m.content IS NOT NULL
                RETURN m.content, m.contentEmbedding
                LIMIT 1
                """
            )
            for record in result:
                content = record["m.content"]
                contentEmbedding = record["m.contentEmbedding"]
                if contentEmbedding is None:
                    print("contentEmbedding is None")
                else:
                    print("Content:", content)
                    print("length content Embedding:", len(contentEmbedding))
        except Exception as e:
            print("An error occurred while fetching data:", e)

def create_vector_index():
    with driver.session() as session:
        try:
            query = """
                CREATE VECTOR INDEX chunk_content_embeddings IF NOT EXISTS
                FOR (n:Chunk) ON (n.contentEmbedding)
                OPTIONS { indexConfig: {
                `vector.dimensions`: 1536,
                `vector.similarity_function`: 'cosine'}}
                """
            session.run(query)

            query = "SHOW VECTOR INDEX"
            result = session.run(query)
            for record in result:
                print(record)
        except Exception as e:
            print("An error occurred:", e)

def main() :
    create_vector_index(URI, user, password)
    update_neo4j_with_embeddings(URI, user, password)
    verify_embeddings(URI, user, password)
    driver.close()

if __name__ == "__main__":
    main()