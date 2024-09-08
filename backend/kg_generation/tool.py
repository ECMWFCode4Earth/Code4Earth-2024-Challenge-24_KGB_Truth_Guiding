"""Tools for human intervention."""
from typing import Optional

from langchain_core.pydantic_v1 import BaseModel, Field

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from typing import Type
from langchain_core.tools import BaseTool
import json
import os

import logging

# Configure the logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SaveInput(BaseModel):
    """Input for saving unresolved chunk"""

    input_info: str = Field(
        ...,
        description="Extract copy of the text that you are unsure how to extract information. Do not change a word.",
    )
    # human_present: bool = Field(..., description="True if human is presence")
    # suggested_answer: str = Field(description="""In case the agent is unsure of the answer, it proposed an answer to the best of its knowledge.
    #                                                 It should be strictly in the format below:
    #                                                     Nodes: ["temperature_measurements", "Property", {}], ["pacific_ocean", "Realm", {"text": "Pacific Ocean"}], ["increase", "Trend", {"direction": "increase"}], ["global_warming", "Phenomenon", {"text": "Global Warming"}]
    #                                                     Relationships: ["temperature_measurements", "hasLocation", "pacific_ocean", {}], ["temperature_measurements", "hasTrend", "increase", {}], ["increase", "isCausedBy", "global_warming", {}]
    #                                                 """)


class Save(BaseTool):
    name: str = "Save_unresolved_chunk"
    args_schema: Type[BaseModel] = SaveInput
    description: str = "This tool is used in case the agent is not sure about the answer. \
                        This will save the input that the agent is unsure about and a human will resolve it later."

    def _run(
        self,
        input_info: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        file_name = "/home/user/large-disk/viet/Code4Earth-2024-Challenge-24/unresolved_by_llm/unresolved.json"

        """Save unresolved query to a file"""
        logging.info("===========Inside tool===========")
        content = {}
        if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
            try:
                # Read the existing content of the file
                with open(file_name, "r") as file:
                    content = json.load(file)
            except json.JSONDecodeError:
                # If the file contains invalid JSON, start with an empty dictionary
                content = {}
        update_info = {
            input_info: {
                "Nodes": [{"name": "", "label": "", "properties": {}}],
                "Relationships": [
                    {"start": "", "end": "", "type": "", "properties": {}}
                ],
            }
            # {
            #     "Suggested answer": suggested_answer,
            #     "Format":
            #         {"Nodes": [{"name": None, "label": None, "properties": {}}],"Relationships": [{"start": None, "end": None, "type": None, "properties": {}}]}
            # }
        }
        # manual_string = """Nodes:"""
        # nodes_input = input(r"""Enter Node in the following format: {name: name_value, label: label_value, property: {property_value}}/...""")
        # nodes_list = nodes_input.split('/')
        # for node in nodes_list:
        #     formatted_node = ast.literal_eval(node)
        #     node_value_string = " " + dict_to_value_string(formatted_node) + " ,"
        #     manual_string += node_value_string
        #     update_info[input_info]["Nodes"].append(formatted_node)
        # manual_string = manual_string[:-1] + "\n" + "Relationships:"
        # relationships_input = input(r"""Enter Relationship in the following format: {start: start_value, end: end_value, type: type_value, property: {property_value}} / ...""")
        # relationships_list = relationships_input.split('/')
        # for relationship in relationships_list:
        #     formatted_relationship = ast.literal_eval(relationship)
        #     relationship_value_string = " " + dict_to_value_string(formatted_relationship) + " ,"
        #     manual_string += relationship_value_string
        #     update_info[input_info]["Relationships"].append(formatted_relationship)
        # Update the content with new information
        content.update(update_info)

        # Write the updated content back to the file
        with open(file_name, "w") as file:
            json.dump(content, file, indent=4)

        return update_info


def dict_to_value_string(data):
    # Extract values from the dictionary
    values = list(data.values())

    # Format the values into a string
    values_string = str(values)

    # Ensure the string is wrapped in triple quotes
    result_string = f'"""{values_string}"""'

    return result_string
