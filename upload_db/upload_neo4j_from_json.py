import json
from neo4j import GraphDatabase
from pathlib import Path
# from dotenv import load_dotenv
import os

# Function to load JSON data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to flatten properties
def flatten_properties(properties):
    flat_properties = {}
    if properties is None:
        return {}
    for key, value in properties.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flat_properties[f"{key}_{sub_key}"] = sub_value
        else:
            flat_properties[key] = value
    return flat_properties

# Function to create nodes and relationships in Neo4j
def write_to_neo4j(uri, user, password, data):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Merge nodes
        for label, entities in data['nodes'].items():
            for entity in entities:
                properties = flatten_properties(entity.get('properties', {}))
                query = f"""
                MERGE (n:{entity["label"]} {{name: $name}})
                """
                if properties:
                    prop_assignments = ', '.join([f"n.{key} = ${key}" for key in properties.keys()])
                    query += f" SET {prop_assignments}"
                if entity["label"] != "__Chunk__":
                    entity_label = entity["label"]
                    parameters = {"name": entity["name"], **properties}
                    query += f" SET n:{entity_label}:__Entity__"
                else:
                    parameters = {"name": entity["name"], **properties}
                session.run(query, parameters)
        
        # Merge relationships
        for relationship in data['relationships']:
            properties = flatten_properties(relationship.get('properties', {}))
            query = f"""
            MATCH (start {{name: $start}})
            MATCH (end {{name: $end}})
            MERGE (start)-[r:{relationship['type']}]->(end)
            """
            if properties:
                prop_assignments = ', '.join([f"r.{key} = ${key}" for key in properties.keys()])
                query += f" SET {prop_assignments}"
            parameters = {"start": relationship["start"], "end": relationship["end"], **properties}
            session.run(query, parameters)
    
    driver.close()
    
    
# Main function
if __name__ == "__main__":
    
    # _ = load_dotenv()
#    load_status = dotenv.load_dotenv("Neo4j-a71aea6b-Created-2024-06-09.txt")
    # if load_status is False:
    #     raise RuntimeError("Environment variables not loaded.")

    
    # Neo4j connection details
    URI = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    # Write to Neo4j
    # Load JSON data

    directory = Path("../assets")
    json_files = [os.path.join(directory,f) for f in os.listdir(directory) if f.endswith('.json')]

    for i, file in enumerate(json_files):
        print(file)
        data = load_json(file)
        write_to_neo4j(URI, user, password, data)
