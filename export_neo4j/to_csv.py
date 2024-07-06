import json
import csv
import os


def extract_to_csv(file):
    if os.path.isfile(file) and os.access(file, os.R_OK):
        # checks if file exists
        print("File exists and is readable")
    else:
        raise Exception("File doesn't exist!")
    with open(file, "r") as file:
        data = json.load(file)
        # Convert nodes to CSV
        with open("nodes.csv", "w", newline="") as nodes_file:
            fieldnames = ["name", "label", "properties"]
            writer = csv.DictWriter(nodes_file, fieldnames=fieldnames)

            writer.writeheader()
            for node_type in data["nodes"]:
                for node in data["nodes"][node_type]:
                    properties = node["properties"]
                    if not properties:
                        properties = None
                    writer.writerow(
                        {
                            "name": node["name"],
                            "label": node["label"],
                            "properties": json.dumps(properties)
                            if properties
                            else None,
                        }
                    )
        # Convert relationships to CSV
        with open("relationships.csv", "w", newline="") as relationships_file:
            fieldnames = ["start", "end", "type", "properties"]
            writer = csv.DictWriter(relationships_file, fieldnames=fieldnames)

            writer.writeheader()
            for relationship in data["relationships"]:
                properties = relationship["properties"]
                if not properties:
                    properties = None
                writer.writerow(
                    {
                        "start": relationship["start"],
                        "end": relationship["end"],
                        "type": relationship["type"],
                        "properties": json.dumps(properties) if properties else None,
                    }
                )
