from ollama import Client


class Ollama:
    def __init__(self, llm_name, num_ctx=8000, host="127.0.0.1:12345") -> None:
        self.llm = llm_name
        self.chat_client = Client(host=host)
        self.num_ctx = num_ctx
        self.tokenizer = None

    def run(self, messages):
        stream = self.chat_client.chat(
            model=self.llm,
            messages=messages,
            stream=False,
            options={"num_ctx": self.num_ctx},
        )
        return stream["message"]["content"]
