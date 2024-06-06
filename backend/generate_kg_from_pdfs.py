from pathlib import Path

from kg_generation.generator import KGGenerator
from langchain_community.document_loaders import PyPDFLoader

data_dir = Path("/home/user/large-disk/ddwf_papers/")
kg_generator = KGGenerator("llama3:70b-instruct-q3_K_L")
labels = None

for file_path in data_dir.iterdir():
    if file_path.suffix == ".pdf":
        print(file_path)
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split(kg_generator.get_text_splitter())
        toy_data = Path("/home/user/large-disk/toy_data")
        for page_number, page in enumerate(pages):
            print(f"Processing page {page_number}")
            text = page.page_content.replace("\n", " ")
            sub_kg = kg_generator.from_text(text, labels)
            kg_generator.add_kg(sub_kg)
            labels = kg_generator.entitydb.get_label_set_as_str()

    kg_generator.save_kg_as_json("../assets/ddwf.json")
