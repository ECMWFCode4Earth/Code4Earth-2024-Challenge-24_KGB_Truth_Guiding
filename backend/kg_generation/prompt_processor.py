import json
import re

from langchain_core.prompts import PromptTemplate

jsonRegex = r"\{.*\}"


class PromptProcessor:
    def __init__(self) -> None:
        self.system_prompt = """You are a data scientist working for a company that is building a graph database. Your task is to extract information from data and convert it into a graph database.
        Provide a set of Nodes in the form [ENTITY_ID, TYPE, PROPERTIES] and a set of relationships in the form [ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, PROPERTIES].
        It is IMPORTANT that the ENTITY_ID_1 and ENTITY_ID_2 exists as nodes with a matching ENTITY_ID. Do not pair any relationship with non-existing nodes. If you can't pair a relationship with a pair of nodes don't add it.
        When you find a node or relationship you want to add try to create a generic TYPE for it that  describes the entity you can also think of it as a label.
        You will be given a list of types that you should try to use when creating the TYPE for a node. If you can't find a type that fits the node you can create a new one.
        NO YAPPING before or after your answers. DO NOT add comments in your answers. Format your answer to strictly follow the rules in the example below.

        Example:
        Data: Alice lawyer and is 25 years old and Bob is her roommate since 2001. Bob works as a journalist. Alice owns a the webpage www.alice.com and Bob owns the webpage www.bob.com.
        Nodes: ["alice", "Person", {"age": 25, "occupation": "lawyer", "name":"Alice"}], ["bob", "Person", {"occupation": "journalist", "name": "Bob"}], ["alice.com", "Webpage", {"url": "www.alice.com"}], ["bob.com", "Webpage", {"url": "www.bob.com"}]
        Relationships: ["alice", "roommate", "bob", {"start": 2021}], ["alice", "owns", "alice.com", {}], ["bob", "owns", "bob.com", {}]
        """
        self.user_prompt_template = PromptTemplate.from_template(
            "Data: {data}\nTypes: {labels}"
        )

    def create_prompt(self, text, labels=None):
        data = text.rstrip()
        if labels is None:
            labels = []
        user_message = self.user_prompt_template.invoke(
            {"data": data, "labels": labels}
        ).to_string()
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]
        return messages

    def process_answer(self, answer_content):
        kg = getNodesAndRelationshipsFromResult([answer_content.replace("\n", " ")])
        labels = getTypesFromDict(kg)
        return kg, labels


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


def getTypesFromDict(result):
    labels = []
    for node in result["nodes"]:
        if node["label"] not in labels:
            labels.append(node["label"])
    return labels


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
