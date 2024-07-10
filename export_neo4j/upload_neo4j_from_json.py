import json
from neo4j import GraphDatabase
from pathlib import Path
from dotenv import load_dotenv
import os
import re


# Function to load JSON data
def load_json(file_path):
    with open(file_path, "r") as file:
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
        for label, entities in data["nodes"].items():
            for entity in entities:
                properties = flatten_properties(entity.get("properties", {}))
                lbl = re.sub('[^a-zA-Z0-9\n\.]', '_', entity["label"])
                query = f"""
                MERGE (n:{lbl} {{name: $name}})
                """
                if properties:
                    prop_assignments = ", ".join(
                        [f"n.{key} = ${key}" for key in properties.keys()]
                    )
                    query += f" SET {prop_assignments}"
                parameters = {
                    "name": entity["name"],
                    "label": entity["label"],
                    **properties,
                }
                session.run(query, parameters)

        # Merge relationships
        for relationship in data["relationships"]:
            properties = flatten_properties(relationship.get("properties", {}))
            type = re.sub('[^a-zA-Z0-9\n\.]', '_', relationship['type'])
            query = f"""
            MATCH (start {{name: $start}})
            MATCH (end {{name: $end}})
            MERGE (start)-[r:{type}]->(end)
            """
            if properties:
                prop_assignments = ", ".join(
                    [f"r.{key} = ${key}" for key in properties.keys()]
                )
                query += f" SET {prop_assignments}"
            parameters = {
                "start": relationship["start"],
                "end": relationship["end"],
                **properties,
            }
            session.run(query, parameters)

    driver.close()


# Main function
if __name__ == "__main__":
    _ = load_dotenv()
    #    load_status = dotenv.load_dotenv("Neo4j-a71aea6b-Created-2024-06-09.txt")
    # if load_status is False:
    #     raise RuntimeError("Environment variables not loaded.")

    # Neo4j connection details
    # URI = os.getenv("NEO4J_URI")
    # user = os.getenv("NEO4J_USERNAME")
    # password = os.getenv("NEO4J_PASSWORD")
    URI = "bolt://localhost:7687"
    user = "neo4j"
    password = "Hoank0906"
    # Write to Neo4j
    # Load JSON data

    # directory = Path("/Users/quocviet.nguyen/Neo4jTuto/json_db")
    directory = Path("/Users/hoang/Neo4j_proj/json_db")
    json_files = [
        os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".json")
    ]

    for file in json_files:
        data = load_json(file)
        write_to_neo4j(URI, user, password, data)
