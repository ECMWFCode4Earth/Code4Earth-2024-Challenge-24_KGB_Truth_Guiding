from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

_ = load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def create_vector_db(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        query = """
                CREATE VECTOR INDEX chunk_content_embeddings IF NOT EXISTS
                FOR (n:Chunk) ON (n.contentEmbedding)
                OPTIONS { indexConfig: {
                `vector.dimensions`: 1536,
                `vector.similarity_function`: 'cosine'}}
                """

        session.run(query)

        query = """
            SHOW VECTOR INDEX
        """

        print(session.run(query))

        query = """
            MATCH (n:Chunk) WHERE n.content IS NOT NULL
            WITH n, genai.vector.encode(
                n.content,
                "OpenAI",
                {
                token: $openAiApiKey
                }) AS vector
            CALL db.create.setNodeVectorProperty(n, "contentEmbedding", vector)
            """
        # params={, "openAiEndpoint": OPENAI_ENDPOINT} )
        params = {"openAiApiKey": OPENAI_API_KEY}
        session.run(query, params)

    driver.close()


if __name__ == "__main__":
    # Neo4j connection details
    URI = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    # create_vector_db(uri=URI, user=user, password=password)
    driver = GraphDatabase.driver(URI, auth=(user, password))

    with driver.session() as session:
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
            print("Content:", content)
            print("length content Embedding:", len(contentEmbedding))
    driver.close()
