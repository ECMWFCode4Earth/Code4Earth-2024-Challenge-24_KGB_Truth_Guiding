from pathlib import Path
import os
from kg_generation.generator import KGGenerator

# from dotenv import load_dotenv

# _ = load_dotenv()


# data_dir = Path("/home/user/large-disk/ddwf_papers/")
# kg_generator = KGGenerator("llama3:70b-instruct-q3_K_L")
labels = None

TXT_FILES = Path("../txt_files")

# Filter the list to include only directories
print(os.getcwd())
files = [
    item
    for item in os.listdir(TXT_FILES)
    if item.endswith(".txt")
]
files = [
    os.path.join(TXT_FILES, file) for file in files
]
print("Files are \n", files)
# file = "/home/user/large-disk/crawled_resources/test/18490-radiation-quantities-ecmwf-model-and-mars/texts/clean_content.txt"

# kg_generator.from_txt_document(file)
for file in files:
    # kg_generator_with_agent = KGGeneratorWithAgent()
    # kg_generator_with_agent.from_txt_document(file)
    print(file)
    # kg_generator = KGGenerator("llama3:70b-instruct-q3_K_L")
    kg_generator = KGGenerator()
    kg_generator.from_txt_document(file)
