import json
from typing import TypedDict, Union, Dict, List
import re

# This is for using OpenAI, might change it later to open-source software
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# This is for implementing agentic llm
from .tool import Save
from .agent import Agent


from .entitydb import Entity, EntityDB

# from .llm_wrapper import Ollama
from .prompt_processor import PromptProcessor
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Document
import os
import logging

# Configure the logging
OUTPUT_FOLDER = os.path.join("../assets")


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Relationship(TypedDict):
    start: str
    end: str
    type: str
    properties: str


class KnowledgeGraph(TypedDict):
    nodes: Dict[str, List[Entity]]
    relationships: List[Relationship]


class KGGenerator:
    def __init__(self) -> None:
        # self.llm = Ollama(llm)
        self.llm = ChatOpenAI(model="gpt-4o-mini")
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
        llm_ans = self.llm.invoke(prompt_messages).content
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

    def from_txt_document(self, file, id_header=None, abbreviations_table = {}):
        path_decomposed = file.split("/")
        # abbreviations_table_path = (
        #     "/".join(path_decomposed[:-2]) + "/tables/abbreviations.json"
        # )
        # try:
        #     with open(abbreviations_table_path, "r") as abbreviations_file:
        #         abbreviations_table = json.load(abbreviations_file)
        # except Exception:
        #     abbreviations_table = {}
        abbreviations_list = [abbr for abbr in abbreviations_table.keys()]
        # header_pattern = re.compile(r"\b\d+\b")
        # for hierarchy in path_decomposed:
        #     match = re.search(header_pattern, hierarchy)
        #     if match:
        #         break
        # header = match.group(0) if match else None
        header = path_decomposed[-1]
        print(header)
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

            node_parser = SentenceSplitter(chunk_size=256, chunk_overlap=28)

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
                os.path.join(OUTPUT_FOLDER, header[:-4]+".json")
            )

    def save_kg_as_json(self, path):
        logging.info("Inside saving file!")
        with open(path, "w") as outfile:
            json.dump(self.kg, outfile, indent=4)


class KGGeneratorWithAgent(KGGenerator):
    def __init__(self):
        self.llm = ChatOpenAI()
        self.prompt_processor = PromptProcessor(for_agent=True)
        self.kg: KnowledgeGraph = {
            "nodes": {"Entity": [], "Chunk": []},
            "relationships": [],
        }
        self.entitydb = EntityDB()

    def from_text(self, text, id, labels=None):
        if not isinstance(text, str):
            text = text.get_content()
        assert isinstance(text, str)
        kg = {"nodes": {}, "relationships": []}

        prompt_messages = self.prompt_processor.create_prompt(text, labels)

        # llm_ans = self.llm.run(prompt_messages)
        system_message = prompt_messages[0]["content"]

        tools = [Save()]
        abot = Agent(self.llm, tools, system=system_message)
        messages = [HumanMessage(content=prompt_messages[1]["content"])]
        llm_ans = abot.graph.invoke({"messages": messages})
        # logging.info("*********** Inside generator.py ************")
        # logging.info(llm_ans["messages"][1].content)

        ai_message = llm_ans["messages"][1].content
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
