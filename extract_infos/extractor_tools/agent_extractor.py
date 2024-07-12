import sys
import re
import json
from backend.kg_generation.llm_wrapper import Ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter


import logging

# Get the directory two levels up
parentdir = "/home/user/large-disk/viet/Code4Earth-2024-Challenge-24"
print(parentdir)
# Add the parent directory to sys.path
sys.path.append(parentdir)


# Configure the logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ExtractAbbreviationWithLLM:
    def __init__(self, save_file, system=None):
        if system is None:
            self.system = r"""
                You are an experienced linguistic who have an eye for detail. You want to extract abbreviations from a document.\
                The abbreviations are always full captial string with the meaning around it. The first letters of the meaning combine abbreviation \
                For example, MHS is the abbreviations of Microwave Humidity Sounder since their first letters are M,H,S \
                Especially, if you see the pattern <Short Name\n Name>, it is likely the table of abbreviations. Look to it closely and extract abbreviations \
                Strictly follow the instructions below for your output:
                - NO YAPPING before or after your answers. DO NOT add any comment or notes in your answers.
                - Format your answers to strictly follow the rules in the example below.
                Here is the example of input and your expected answer
                For example:
                Input:
                    MHS (Microwave Humidity Sounder) and AMSU-A (Advanced Microwave Sounding Sounding Unit-A)
                Your answer:
                    {"MHS": "Microwave Humidity Sounder",
                     "AMSU-A": "Advanced Microwave Sounding Sounding Unit-A"}
            """
        else:
            self.system = system
        self.model = Ollama("llama3:70b-instruct-q3_K_L")
        self.save_file = save_file

    def execute(self, prompt: str):
        messages = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": prompt},
        ]
        answer = self.model.run(messages)
        formatted_answer = re.compile(r"\{[^{}]*\}").findall(answer)[0]
        formatted_answer = f"""{formatted_answer}"""
        abbr_from_prompt = json.loads(formatted_answer)
        abbreviations = {}
        try:
            with open(self.save_file, "r") as file:
                abbreviations = json.load(file)
        except Exception:
            abbreviations = {}

        abbreviations.update(abbr_from_prompt)
        logging.info("=====================")
        logging.info(abbreviations)
        with open(self.save_file, "w") as file:
            json.dump(abbreviations, file)

    def extract_from_txt_document(self, file):
        with open(file) as f:
            content = f.read()
            text_splitter = RecursiveCharacterTextSplitter(
                # Set a really small chunk size, just to show.
                chunk_size=2000,
                chunk_overlap=200,
                length_function=len,
                is_separator_regex=False,
            )
            texts = text_splitter.split_text(content)
            for id, text in enumerate(texts):
                self.execute(text)
