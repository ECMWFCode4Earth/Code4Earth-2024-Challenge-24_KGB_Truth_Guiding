from __future__ import annotations

import json
import re

from langchain_core.prompts import PromptTemplate


jsonRegex = r"\{.*\}"


class PromptProcessor:
    def __init__(self, for_agent=False) -> None:
        self.system_prompt = """"""

        if for_agent:
            self.system_prompt = """You are a data scientist working for a company that is building a knowledge graph of Earth and Environment Science.
            Your task is to extract information from scientific documents and convert it into a knowledge graph. Follow these guidelines:
                - Provide nodes as: ["entity_id": str, "Type": str, "properties": dict()]
                - Provide relationships as: ["entity_id_1": str, "hasRelationship": str, "entity_id_2": str, "properties": dict()]
                - Ensure "entity_id_1" and "entity_id_2" exist as nodes with a matching entity ID.
                - Do not add relationships with non-existing nodes.
                - Use provided types when possible; create new ones if necessary.
                - Entity IDs must be lowercase, no special characters or spaces, with words separated by "_".
                - NO YAPPING before or after your answers. DO NOT add any comment or notes in your answers.
                - Format your answers to strictly follow the rules in the example below.
            If you don't know the answer, say you are unsure and ask for human intervention.
            You have access to a tool. REMEMBER: You ONLY use the tool when you need to ask for human intervention.

            Your workflow follows the following steps: Data -> Thought -> Action -> Action Input.
            Remember that Action should by only "Call the verifer" or "Ask for human intervention"

            Two examples for you to understand the workflow of the process:
            Example 1 - If you are sure about the answer:
            Input Data:
                Text: Temperature measurements taken from the Pacific Ocean show an increase due to global warming.
                Types: [Process, Property]

            Thought: I'm sure about the answer and will return the answer in the following format:
                Nodes: ["temperature_measurements", "Property", {}], ["pacific_ocean", "Realm", {"text": "Pacific Ocean"}], ["increase", "Trend", {"direction": "increase"}], ["global_warming", "Phenomenon", {"text": "Global Warming"}]
                Relationships: ["temperature_measurements", "hasLocation", "pacific_ocean", {}], ["temperature_measurements", "hasTrend", "increase", {}], ["increase", "isCausedBy", "global_warming", {}]
            Action: Call the verifier with the following prompt:
                Input Data:
                    Text: Temperature measurements taken from the Pacific Ocean show an increase due to global warming.
                    Type: [Process, Property]
                Extracted information:
                    Nodes: ["temperature_measurements", "Property", {}], ["pacific_ocean", "Realm", {"text": "Pacific Ocean"}], ["increase", "Trend", {"direction": "increase"}], ["global_warming", "Phenomenon", {"text": "Global Warming"}]
                    Relationships: ["temperature_measurements", "hasLocation", "pacific_ocean", {}], ["temperature_measurements", "hasTrend", "increase", {}], ["increase", "isCausedBy", "global_warming", {}]

            Example 2 - If you are unsure about the answer:
            Input Data:
                Text: Temperature measurements taken from the Pacific Ocean show an increase due to global warming.
                Types: [Process, Property]

            Thought: I'm not sure how to extract information from this data.
            Action: Call a function to save unresolved chunk into a file and a human will resolve it later.
            Action input:
                Temperature measurements taken from the Pacific Ocean show an increase due to global warming.

            """
        else:
            self.system_prompt = """You are a data scientist working for a company that is building a knowledge graph of Earth and Environment Science.
            Your task is to extract information from scientific documents and convert it into a knowledge graph. Follow these guidelines:
                - Provide nodes as: ["entity_id": str, "Type": str, "properties": dict()]
                - Provide relationships as: ["entity_id_1": str, "hasRelationship": str, "entity_id_2": str, "properties": dict()]
                - Ensure "entity_id_1" and "entity_id_2" exist as nodes with a matching entity ID.
                - Do not add relationships with non-existing nodes.
                - Use provided types when possible; create new ones if necessary.
                - Entity IDs must be uppercase in the first character of each word, no special characters or spaces, with words separated by "_".
                - NO YAPPING before or after your answers. DO NOT add any comment or notes in your answers.
                - Format your answers to strictly follow the rules in the example below.
            Example:
                Input Data:
                    Text: Temperature measurements taken from the Pacific Ocean show an increase due to global warming.
                    Type: [Process, Property]
                Extracted information:
                    Nodes: ["temperature_measurements", "Property", {}], ["pacific_ocean", "Realm", {"text": "Pacific Ocean"}], ["increase", "Trend", {"direction": "increase"}], ["global_warming", "Phenomenon", {"text": "Global Warming"}]
                    Relationships: ["temperature_measurements", "hasLocation", "pacific_ocean", {}], ["temperature_measurements", "hasTrend", "increase", {}], ["increase", "isCausedBy", "global_warming", {}]            """

        self.user_prompt_template = PromptTemplate.from_template(
            "Data: {data}\nTypes: [{labels}]"
        )

    def create_prompt(self, text: str, labels: str | None = None):
        if labels is None:
            labels = ""
        user_message = self.user_prompt_template.invoke(
            {"data": text, "labels": labels}
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
        # print(row)
        parsing = re.match(regex, row, flags=re.S)
        if parsing is None:
            # print(parsing)
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
