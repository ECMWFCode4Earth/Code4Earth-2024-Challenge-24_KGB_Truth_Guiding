

from neo4j import GraphDatabase
import openai
import os
# from dotenv import load_dotenv


def encode_text(text):
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def create_vector_index_chunk(driver):
    with driver.session() as session:
        try:
            query = """
                CREATE VECTOR INDEX chunk_content_embeddings IF NOT EXISTS
                FOR (n:__Chunk__) ON (n.contentEmbedding)
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

def update_neo4j_with_embeddings_chunk(driver):
    with driver.session() as session:
        try:
            result = session.run("MATCH (n:__Chunk__) WHERE n.content IS NOT NULL RETURN n.content, ID(n) AS id")
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
                        "MATCH (n:__Chunk__) WHERE ID(n) = $id SET n.contentEmbedding = $embedding",
                        id=node_id, embedding=embedding
                    )
                    print(f"Set embedding for node ID {node_id}")
                else:
                    print(f"No embedding returned for node ID {node_id}")
        except Exception as e:
            print("An error occurred:", e)

def verify_embeddings_chunk(driver):
    with driver.session() as session:
        try:
            result = session.run(
                """
                MATCH (m:__Chunk__)
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

def create_vector_index_entity(driver):
    with driver.session() as session:
        try:
            query = """
                CREATE VECTOR INDEX entity_embeddings IF NOT EXISTS
                FOR (n:__Entity__) ON (n.entityEmbedding)
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

def update_neo4j_with_embeddings_entity(driver):
    with driver.session() as session:
        try:
            result = session.run("MATCH (n:__Entity__) WHERE n.name IS NOT NULL RETURN n.name, ID(n) AS id, n.text, n.description")
            for record in result:
                name = record["n.name"]
                node_id = record["id"]
                # Optional checks for n.text and n.description
                text = record["n.text"] if "n.text" in record and record["n.text"] else None
                description = record["n.description"] if "n.description" in record and record["n.description"] else None
                
                if not name:
                    print(f"Skipping empty name for node ID {node_id}")
                    continue
                text_safe = text or ''
                description_safe = description or ''

                try:
                    embedding = encode_text(name + text_safe + description_safe)
                except Exception as e:
                    print(f"Error getting embedding for node ID {node_id}: {e}")
                    continue
                
                if embedding:
                    session.run(
                        "MATCH (n:__Entity__) WHERE ID(n) = $id SET n.entityEmbedding = $embedding",
                        id=node_id, embedding=embedding
                    )
                    print(f"Set embedding for node ID {node_id}")
                else:
                    print(f"No embedding returned for node ID {node_id}")
        except Exception as e:
            print("An error occurred:", e)

def verify_embeddings_entity(driver):
    with driver.session() as session:
        try:
            result = session.run(
                """
                MATCH (m:__Entity__)
                WHERE m.name IS NOT NULL
                RETURN m.name, m.entityEmbedding
                LIMIT 1
                """
            )
            for record in result:
                name = record["m.name"]
                entityEmbedding = record["m.entityEmbedding"]
                if entityEmbedding is None:
                    print("entityEmbedding is None")
                else:
                    print("Content:", name)
                    print("length content Embedding:", len(entityEmbedding))
        except Exception as e:
            print("An error occurred while fetching data:", e)


def create_vector_index_community(driver):
    with driver.session() as session:
        try:
            query = """
                CREATE VECTOR INDEX community_embeddings IF NOT EXISTS
                FOR (n:__Community__) ON (n.communityEmbedding)
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

def update_neo4j_with_embeddings_community(driver):
    with driver.session() as session:
        try:
            result = session.run("MATCH (n:__Community__) WHERE n.summary IS NOT NULL RETURN n.summary, ID(n) AS id")
            for record in result:
                summary = record["n.summary"]
                node_id = record["id"]
                
                if not summary:
                    print(f"Skipping empty summary for node ID {node_id}")
                    continue
                try:
                    embedding = encode_text(summary)
                except Exception as e:
                    print(f"Error getting embedding for node ID {node_id}: {e}")
                    continue
                
                if embedding:
                    session.run(
                        "MATCH (n:__Community__) WHERE ID(n) = $id SET n.communityEmbedding = $embedding",
                        id=node_id, embedding=embedding
                    )
                    print(f"Set embedding for node ID {node_id}")
                else:
                    print(f"No embedding returned for node ID {node_id}")
        except Exception as e:
            print("An error occurred:", e)

def verify_embeddings_community(driver):
    with driver.session() as session:
        try:
            result = session.run(
                """
                MATCH (m:__Community__)
                WHERE m.summary IS NOT NULL
                RETURN m.summary, m.communityEmbedding
                LIMIT 1
                """
            )
            for record in result:
                summary = record["m.summary"]
                communityEmbedding = record["m.communityEmbedding"]
                if communityEmbedding is None:
                    print("communityEmbedding is None")
                else:
                    print("Content:", summary)
                    print("length content Embedding:", len(communityEmbedding))
        except Exception as e:
            print("An error occurred while fetching data:", e)



def main() :
    # _ = load_dotenv()
    # Set up OpenAI API key
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = OPENAI_API_KEY

    # Neo4j configuration
    URI = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    driver = GraphDatabase.driver(URI, auth=(user, password))

    create_vector_index_chunk(driver)
    update_neo4j_with_embeddings_chunk(driver)
    verify_embeddings_chunk(driver)

    create_vector_index_entity(driver)
    update_neo4j_with_embeddings_entity(driver)
    verify_embeddings_entity(driver)

    create_vector_index_community(driver)
    update_neo4j_with_embeddings_community(driver)
    verify_embeddings_community(driver)

    driver.close()

if __name__ == "__main__":
    main()