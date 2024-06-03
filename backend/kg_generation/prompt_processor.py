from __future__ import annotations

import json
import re

from langchain_core.prompts import PromptTemplate

jsonRegex = r"\{.*\}"


class PromptProcessor:
    def __init__(self) -> None:
        self.system_prompt = """You are a data scientist working for a company that is building a knowledge graph of Earth and Environment Science.
        Your task is to extract information from scientific documents and convert it into a knowledge graph. Follow these guidelines:
            - Provide nodes as: ["entity_id": str, "Type": str, "properties": dict()]
            - Provide relationships as: ["entity_id_1": str, "hasRelationship": str, "entity_id_2": str, "properties": dict()]
            - Ensure "entity_id_1" and "entity_id_2" exist as nodes with a matching entity ID.
            - Do not add relationships with non-existing nodes.
            - Create a generic "type" for nodes, referring to the http://sweetontology.net/sweetAll ontology for available types and relationships.
            - Use provided types when possible; create new ones if necessary.
            - Entity IDs must be lowercase, no special characters or spaces, with words separated by "_".
            - NO YAPPING before and after reponses. No comments or extra text in your answers.
        Example:
        Data: Temperature measurements taken from the Pacific Ocean show an increase due to global warming.
        Types: [Process, Property]
        Nodes: ["temperature_measurements", "Property", {}], ["pacific_ocean", "Realm", {"name": "Pacific Ocean"}], ["increase", "Trend", {"direction": "increase"}], ["global_warming", "Phenomenon", {"name": "Global Warming"}]
        Relationships: ["temperature_measurements", "hasLocation", "pacific_ocean", {}], ["temperature_measurements", "hasTrend", "increase", {}], ["increase", "isCausedBy", "global_warming", {}]
        """
        self.user_prompt_template = PromptTemplate.from_template(
            "Data: {data}\nTypes: [{labels}]"
        )

    def create_prompt(self, text: str, labels: str | None = None):
        data = text.rstrip()
        if labels is None:
            labels = ""
        user_message = self.user_prompt_template.invoke(
            {"data": data, "labels": labels}
        ).to_string()
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]
        return messages

    def process_answer(self, answer_content: str):
        kg = getNodesAndRelationshipsFromResult([answer_content.replace("\n", " ")])
        return kg


def getNodesAndRelationshipsFromResult(result):
    regex = r"Nodes:\s*(.*?)\s*Relationships:\s*(.*)"
    internalRegex = r"\[(.*?)\]"
    nodes = []
    relationships = []
    for row in result:
        print(row)
        parsing = re.match(regex, row, flags=re.S)
        if parsing is None:
            print(parsing)
            continue
        rawNodes = str(parsing.group(1))
        rawRelationships = parsing.group(2)
        nodes.extend(re.findall(internalRegex, rawNodes))
        relationships.extend(re.findall(internalRegex, rawRelationships))

    result = dict()
    result["nodes"] = []
    result["relationships"] = []
    result["nodes"].extend(nodesTextToListOfDict(nodes))
    result["relationships"].extend(relationshipTextToListOfDict(relationships))
    return result


def nodesTextToListOfDict(nodes):
    result = []
    for node in nodes:
        nodeList = node.split(",")
        if len(nodeList) < 2:
            continue

        name = nodeList[0].strip().replace('"', "")
        label = nodeList[1].strip().replace('"', "")
        properties = re.search(jsonRegex, node)
        if properties is None:
            properties = "{}"
        else:
            properties = properties.group(0)
        properties = properties.replace("True", "true")
        try:
            properties = json.loads(properties)
        except ValueError:
            properties = {}
        result.append({"name": name, "label": label, "properties": properties})
    return result


def relationshipTextToListOfDict(relationships):
    result = []
    for relation in relationships:
        relationList = relation.split(",")
        if len(relation) < 3:
            continue
        start = relationList[0].strip().replace('"', "")
        end = relationList[2].strip().replace('"', "")
        label = relationList[1].strip().replace('"', "")

        properties = re.search(jsonRegex, relation)
        if properties is None:
            properties = "{}"
        else:
            properties = properties.group(0)
        properties = properties.replace("True", "true")
        try:
            properties = json.loads(properties)
        except ValueError:
            properties = {}
        result.append(
            {"start": start, "end": end, "type": label, "properties": properties}
        )
    return result
