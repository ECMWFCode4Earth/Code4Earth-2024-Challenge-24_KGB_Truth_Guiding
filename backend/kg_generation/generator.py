import json
from typing import TypedDict, Dict, List
import re
import numpy as np
import sys
import os


# This is for using OpenAI, might change it later to open-source software

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langchain_core.messages import HumanMessage
# from dotenv import load_dotenv
# _ = load_dotenv()

# This is for implementing agentic llm
from .tool import Save
from .agent import Agent


from .entitydb import Entity, EntityDB

# from .text_chunk_entitydb import Chunk
from .llm_wrapper import Ollama
from .prompt_processor import PromptProcessor
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Document

import logging

# Configure the logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(current_path)
sys.path.append(parent_path)


class Relationship(TypedDict):
    start: str
    end: str
    type: str
    properties: str


class KnowledgeGraph(TypedDict):
    nodes: Dict[str, List[Entity]]
    relationships: List[Relationship]


class KGGenerator:
    def __init__(self, llm) -> None:
        self.llm = Ollama(llm)
        self.prompt_processor = PromptProcessor(for_agent=False)
        self.kg: KnowledgeGraph = {
            "nodes": {"Entity": [], "Chunk": []},
            "relationships": [],
        }
        self.entitydb = EntityDB()

    # def get_text_splitter(self):
    #     return self.prompt_processor.text_splitter

    def from_text(self, text, id, labels=None):
        if not isinstance(text, str):
            text = text.get_content()
        assert isinstance(text, str)
        kg = {"nodes": {}, "relationships": []}

        prompt_messages = self.prompt_processor.create_prompt(text, labels)
        llm_ans = self.llm.run(prompt_messages)
        kg_temp = self.prompt_processor.process_answer(llm_ans)
        kg["nodes"]["Entity"] = kg_temp["nodes"]
        kg["relationships"] = kg_temp["relationships"]
        for node in kg["nodes"]["Entity"]:
            kg["relationships"].append(
                Relationship(
                    start=node["name"], end=id, type="APPEARED_IN", properties=None
                )
            )
        kg["nodes"]["Chunk"] = [
            {"name": id, "label": "Chunk", "properties": {"content": text}}
        ]
        return kg

    def add_kg(self, kg: KnowledgeGraph):
        self.kg["relationships"] += kg["relationships"]
        self.kg["nodes"]["Chunk"] += kg["nodes"]["Chunk"]

        for node in kg["nodes"]["Entity"]:
            self.entitydb.add(node)
        self.kg["nodes"]["Entity"] = self.entitydb.get_node_list()

    def from_txt_document(self, file, id_header=None):
        path_decomposed = file.split("/")
        abbreviations_table_path = (
            "/".join(path_decomposed[:-2]) + "/tables/abbreviations.json"
        )
        try:
            with open(abbreviations_table_path, "r") as abbreviations_file:
                abbreviations_table = json.load(abbreviations_file)
        except Exception:
            abbreviations_table = {}
        abbreviations_list = [abbr for abbr in abbreviations_table.keys()]
        header_pattern = re.compile(r"\b\d+\b")
        for hierarchy in path_decomposed:
            match = re.search(header_pattern, hierarchy)
            if match:
                break
        header = match.group(0) if match else None
        with open(file) as f:
            content = f.read()
            chunk_id_list = []
            # text_splitter = RecursiveCharacterTextSplitter(
            #     # Set a really small chunk size, just to show.
            #     chunk_size=1000,
            #     chunk_overlap=200,
            #     length_function=len,
            #     is_separator_regex=False
            # )
            # texts = text_splitter.create_documents([content])

            node_parser = SentenceSplitter(chunk_size=256, chunk_overlap=32)

            texts = node_parser.get_nodes_from_documents(
                [Document(text=content)], show_progress=False
            )

            labels = None
            max_length = len(str(len(texts)))
            recorded_abbr = []
            for id, text in enumerate(texts):
                padded_id = header + "___" + str(id).zfill(max_length)
                chunk_id_list.append(padded_id)
                sub_kg = self.from_text(text, padded_id, labels)

                for node in sub_kg["nodes"]["Entity"]:
                    if node["name"].upper() in abbreviations_list:
                        node["properties"]["text"] = abbreviations_table[
                            node["name"].upper()
                        ]
                        recorded_abbr.append(node["name"].upper())

                for abbr in abbreviations_list:
                    if abbr not in recorded_abbr:
                        sub_kg["nodes"]["Entity"].append(
                            {
                                "name": abbr,
                                "label": "__unknown__",
                                "properties": {"text": abbreviations_table[abbr]},
                            }
                        )

                self.add_kg(sub_kg)
                # logging.info("========Print out KG over time=========")
                # logging.info(self.kg)
                labels = self.entitydb.get_label_set_as_str()
            for i in range(len(chunk_id_list) - 1):
                self.kg["relationships"].append(
                    {
                        "start": chunk_id_list[i],
                        "end": chunk_id_list[i + 1],
                        "type": "NEXT_TO",
                        "properties": {},
                    }
                )
            self.save_kg_as_json(
                f"/home/user/large-disk/crawled_resources/test/{header}_file.json"
            )

    def save_kg_as_json(self, path):
        logging.info("Inside saving file!")
        with open(path, "w") as outfile:
            json.dump(self.kg, outfile, indent=4)


def select_examples(query, top_k=3):
    lookup_file = "/home/user/large-disk/viet/Code4Earth-2024-Challenge-24/unresolved_by_llm/unresolved.json"
    embeddings = OpenAIEmbeddings()
    with open(lookup_file) as file:
        lookup_table = json.load(file)
    scores = []
    for text, extracted_info in lookup_table.items():
        embedded_text = embeddings.embed_query(text)
        embedded_query = embeddings.embed_query(query)
        cosine_similarity = np.array(embedded_text) @ np.array(embedded_query).T
        scores.append((cosine_similarity, text, extracted_info))
    logging.info(len(scores))
    return sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]


class KGGeneratorWithAgent(KGGenerator):
    def __init__(self, for_agent=True):
        self.llm = ChatOpenAI()
        self.for_agent = for_agent
        self.prompt_processor = PromptProcessor(for_agent)
        self.kg: KnowledgeGraph = {
            "nodes": {"Entity": [], "Chunk": []},
            "relationships": [],
        }
        self.entitydb = EntityDB()

    def from_text(self, text, id, labels=None):
        examples = select_examples(text.get_content())
        list_of_extracted_info_examples = []
        for example in examples:
            list_of_extracted_info_examples.append(example[1:])

        template_for_example = """
            Input Data:
                Text: {text}
                Type: [Process, Property]
            Extracted information:
                Nodes: {nodes}
                Relationships: {relationships}
            \n
        """

        examples = ""
        for text, info in list_of_extracted_info_examples:
            formatted_example = template_for_example.format(
                text=text,
                nodes=str(info["Nodes"]),
                relationships=str(info["Relationships"]),
            )

            examples += formatted_example

        if not isinstance(text, str):
            text = text.get_content()
        assert isinstance(text, str)
        kg = {"nodes": {}, "relationships": []}

        prompt_messages = self.prompt_processor.create_prompt(text, labels, examples)

        ai_message = ""
        # llm_ans = self.llm.run(prompt_messages)
        system_message = prompt_messages[0]["content"]
        if self.for_agent:
            tools = [Save()]
            abot = Agent(self.llm, tools, system=system_message)
            messages = [HumanMessage(content=prompt_messages[1]["content"])]
            llm_ans = abot.graph.invoke({"messages": messages})
            ai_message = llm_ans["messages"][1].content

        else:
            llm = ChatOpenAI()
            llm_ans = llm.invoke(prompt_messages)
            ai_message = llm_ans.content
        # logging.info("*********** Inside generator.py ************")
        # logging.info(llm_ans["messages"][1].content)

        kg_temp = self.prompt_processor.process_answer(ai_message)

        kg["nodes"]["Entity"] = kg_temp["nodes"]
        kg["relationships"] = kg_temp["relationships"]
        for node in kg["nodes"]["Entity"]:
            kg["relationships"].append(
                Relationship(
                    start=node["name"], end=id, type="APPEAR_IN", properties=None
                )
            )
        kg["nodes"]["Chunk"] = [
            {"name": id, "label": "Chunk", "properties": {"content": text}}
        ]

        return kg


# if __name__ == "__main__":
#     examples = select_examples(text)
#     list_of_extracted_info_examples = []
#     print(examples[0][1])
#     print(examples[0][2])
#     for example in examples:
#         list_of_extracted_info_examples.append(example[1:])

#     print(list_of_extracted_info_examples)
