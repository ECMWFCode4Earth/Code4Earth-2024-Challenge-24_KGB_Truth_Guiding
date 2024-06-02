from .llm_wrapper import Ollama
from .prompt_processor import PromptProcessor


class KGGenerator:
    def __init__(self, llm) -> None:
        self.llm = Ollama(llm)
        self.prompt_processor = PromptProcessor()

    def from_text(self, text, labels=None):
        prompt_messages = self.prompt_processor.create_prompt(text, labels)
        llm_ans = self.llm.run(prompt_messages)
        kg, labels = self.prompt_processor.process_answer(llm_ans)
        return kg, labels


def merge_kgs(kg1, kg2):
    for k, v in kg2.items():
        if k in kg1:
            kg1[k] += v
        else:
            kg1[k] = v
    return kg1
