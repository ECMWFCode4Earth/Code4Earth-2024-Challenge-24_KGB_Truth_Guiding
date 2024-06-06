import json
from typing import TypedDict

from .entitydb import Entity, EntityDB
from .llm_wrapper import Ollama
from .prompt_processor import PromptProcessor


class Relationship(TypedDict):
    start: str
    end: str
    type: str
    properties: str


class KnowledgeGraph(TypedDict):
    nodes: list[Entity]
    relationships: list[Relationship]


class KGGenerator:
    def __init__(self, llm) -> None:
        self.llm = Ollama(llm)
        self.prompt_processor = PromptProcessor(self.llm.tokenizer)
        self.kg: KnowledgeGraph = {"nodes": [], "relationships": []}
        self.entitydb = EntityDB()

    def get_text_splitter(self):
        return self.prompt_processor.text_splitter

    def from_text(self, text, labels=None):
        prompt_messages = self.prompt_processor.create_prompt(text, labels)
        llm_ans = self.llm.run(prompt_messages)
        kg = self.prompt_processor.process_answer(llm_ans)
        return kg

    def add_kg(self, kg: KnowledgeGraph):
        if "relationships" not in self.kg:
            self.kg["relationships"] = kg["relationships"]
        else:
            self.kg["relationships"] += kg["relationships"]

        for node in kg["nodes"]:
            self.entitydb.add(node)
        self.kg["nodes"] = self.entitydb.get_node_list()

    def save_kg_as_json(self, path):
        with open(path, "w", encoding="utf-8") as outfile:
            json.dump(self.kg, outfile, indent=4)
