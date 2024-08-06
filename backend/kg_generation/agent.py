from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage
from dotenv import load_dotenv
import logging

_ = load_dotenv()


# Configure the logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class Agent:
    def __init__(self, model, tools, system=""):
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_llm)
        graph.add_node("verifier", self.verify)
        graph.add_node("intervention", self.intervention)
        graph.add_conditional_edges(
            "llm", self.exists_action, {False: "verifier", True: "intervention"}
        )

        graph.add_edge("intervention", END)
        graph.add_edge("verifier", END)
        graph.set_entry_point("llm")
        self.graph = graph.compile()
        self.state: AgentState = [system]
        self.tools = {t.name: t for t in tools}
        logging.info(f"Agent has these tools: {self.tools}")
        self.model = model.bind_tools(tools)

    # def action_processor(answer: str):
    #     lines = answer.split('\n')
    #     action_taken_pattern = r"\bACTION_TAKEN\b"
    #     action_input_pattern = r"\bACTION_INPUT\b"
    #     action_taken =
    #     for tool in self.tools:
    #         if tool.name in action:
    #             return tool

    def exists_action(self, state: AgentState):
        result = state["messages"][-1]
        return len(result.tool_calls) > 0

    def verify(self, state: AgentState):
        logging.info("=======Inside verify=======")
        messages = state["messages"][-1]
        logging.info(messages)
        system = SystemMessage(
            content="""You are a very experienced linguistic and your \
            job is to verify the extraction of entity and relation \
            from data. In the next, you will take a prompt with input data and extracted information.\
            If extracted information is correct, return only the extracted information.\
            Otherwise, correct it and return in the format of extracted information. \
            REMEMBER, always return in the strict format of extracted information. \
            For example:
            """
        )
        # if self.system:
        #     messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke([system] + [messages])

        logging.info(message)
        return {"messages": [message]}

    def call_llm(self, state: AgentState):
        messages = [state["messages"][-1]]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        logging.info(message)
        return {"messages": [message]}

    def intervention(self, state: AgentState):
        logging.info("======Inside intervention======")
        logging.info(state["messages"][-1])
        tool_calls = state["messages"][-1].tool_calls
        results = []
        logging.info(tool_calls)
        for t in tool_calls:
            print(f"Calling: {t}")
            if t["name"] not in self.tools:  # check for bad tool name from LLM
                print("\n ....bad tool name....")
                result = "bad tool name, retry"  # instruct LLM to retry if bad
            else:
                logging.info("======================")
                logging.info(t["name"])
                logging.info(t["args"])
                result = self.tools[t["name"]].invoke(t["args"])
            results.append(
                ToolMessage(tool_call_id=t["id"], name=t["name"], content=str(result))
            )
        print("Back to the model!")
        return {"messages": results}

    # def execute(prompt: str):
    #     self.state +=  [promt]
    #     llm_answer = self.model.run(prompt)
    #     tool, tool_args =  self.process_action(llm_answer)


class AgentOllamaState(TypedDict):
    messages: Annotated[list[str], operator.add]


# class AgentOllamaExtractAbbreviation:
#     def __init__(self, model, tools, system=""):
#         self.model = model
#         self.tools = tools
#         self.system = system
#         self.state = []

#     def execute(prompt: str):
#         result = model.run(prompt)
#         message = self.state[-1]


# class AgentOllama:
#     def __init__(self, model, tools, system=""):
#         self.model = model
#         self.tools = tools
#         self.system = system
#         self.state = []

#     def sure_about_answer(self, state: AgentState):
#         result = state[-1]

#         return 'human intervention' not in result.content

#     def process_answer(self, answer):
#         pass

#     def verify(self, state: AgentState):
#         messages = state[-1]
#         system = SystemMessage(
#             content="""You are a very experienced linguistic and your \
#             job is to verify the extraction of entity and relation \
#             from data. In the next, you will take a prompt with input data and extracted information.\
#             If extracted information is correct, return only the extracted information.\
#             Otherwise, correct it and return in the format of extracted information.
#             REMEMBER, always return in the strict format of extracted information.
#             """
#         )
#         # if self.system:
#         #     messages = [SystemMessage(content=self.system)] + messages
#         message = self.model.invoke([system] + [messages])

#         return {'messages': [message]}

#     def call_llm(self, state: AgentState):
#         messages = [state[-1]]
#         if self.system:
#             messages = [SystemMessage(content=self.system)] + messages
#         output = self.model.run(messages)

#         return output

#     def intervention(self, state: AgentState):
#         tool_calls = state[-1].tool_calls
#         results = []
#         for t in tool_calls:
#             print(f"Calling: {t}")
#             if not t['name'] in self.tools:      # check for bad tool name from LLM
#                 print("\n ....bad tool name....")
#                 result = "bad tool name, retry"  # instruct LLM to retry if bad
#             else:
#                 result = self.tools[t['name']].invoke(t['args'])
#             results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
#         print("Back to the model!")
#         return {'messages': results}

#     def execute(prompt: str):
#         self.state += [promt]
#         llm_answer = self.call_llm(self.state)
#         tool, tool_args = self.process_action(llm_answer)
