from pathlib import Path
import os
from kg_generation.generator import KGGeneratorWithAgent

from dotenv import load_dotenv

_ = load_dotenv()


data_dir = Path("/home/user/large-disk/ddwf_papers/")
# kg_generator = KGGenerator("llama3:70b-instruct-q3_K_L")
labels = None

directory = Path("/home/user/large-disk/crawled_resources/test/")

# included_folder = ["18490", "16584", "13562", "11700"]
included_folder = ["18490"]


items = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
items = [item for item in items if item[:5] in included_folder]

# Filter the list to include only directories
folders = [item for item in items if os.path.isdir(os.path.join(directory, item))]

files = [
    os.path.join(os.path.join(directory, folder), "texts/clean_content.txt")
    for folder in folders
]

print("Files are \n", files)
# file = "/home/user/large-disk/crawled_resources/test/18490-radiation-quantities-ecmwf-model-and-mars/texts/clean_content.txt"

# kg_generator.from_txt_document(file)
for file in files:
    kg_generator_with_agent = KGGeneratorWithAgent(for_agent=False)
    kg_generator_with_agent.from_txt_document(file)
    # kg_generator = KGGenerator("llama3:70b-instruct-q3_K_L")
    # kg_generator.from_txt_document(file)
