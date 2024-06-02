from ollama import Client


class Ollama:
    def __init__(self, llm_name, host="127.0.0.1:12345") -> None:
        self.llm = llm_name
        self.chat_client = Client(host=host)

    def run(self, messages):
        stream = self.chat_client.chat(model=self.llm, messages=messages, stream=False)
        return stream["message"]["content"]
