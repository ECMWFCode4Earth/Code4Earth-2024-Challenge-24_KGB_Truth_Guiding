import fitz
import ollama

doc = fitz.open("example.pdf")
for pageNumber, page in enumerate(doc.pages(), start=1):
    if pageNumber > 2 and pageNumber < 10:
        text = page.get_text().encode("utf8")
        with open(f"texts/output_{pageNumber}.txt", "wb") as out:
            out.write(text)  # write text of page
            out.write(bytes((12,)))  # write page delimiter (form feed 0x0C)


system_promt = "You are a helpful Natural Language Processing expert who extracts relevant information and store them on a Knowledge Graph"

user_promt = """From the technical report on Methods for assessing the impact of current and future components of the global observing system, extract the following Entities & relationships described in the mentioned format
0. ALWAYS FINISH THE OUTPUT. Never send partial responses
1. First, look for these Entity types in the text and generate as comma-separated format similar to entity type.
   `id` property of each entity must be alphanumeric such as A1.01 and must be unique among the entities. You will be referring this property to define the relationship between entities. Do not create new entity types that aren't mentioned below. Document must be summarized and stored inside Case entity under `summary` property. You will have to generate as many entities as needed as per the types below:
    Entity Types:
    label:'Approach',id:string,Name:string, Abbreviation:string //Approach
    label:'System',id:string,Name:string //Patient mentioned in the case
    label:'Authority',id:string,Name:string, Abbreviation: string //Symptom Entity; `id` property is the name of the symptom, in lowercase & camel-case & should always start with an alphabet
    label: 'Requirement', id:string, Abbreviation:string // Requirement
    label: 'Paper', id:string, author: string // Paper

3. Next generate each relationships as triples of head, relationship and tail. To refer the head and tail entity, use their respective `id` property. Relationship property should be mentioned within brackets as comma-separated. They should follow these relationship types below. You will have to generate as many relationships as needed as defined below:
    Relationship types:
    Authority.Name|SUPPORT|Approach.Name
    Paper.Name|CREATE|Approach.Name
    System.Name|CONDUCT|Approach.Name

    # case|FOR|person
    # person|HAS_SYMPTOM{when:string,frequency:string,span:string}|symptom //the properties inside HAS_SYMPTOM gets populated from the Case sheet
    # person|HAS_DISEASE{when:string}|disease //the properties inside HAS_DISEASE gets populated from the Case sheet
    # symptom|SEEN_ON|chest
    # disease|AFFECTS|heart
    # person|HAS_DIAGNOSIS|diagnosis
    # diagnosis|SHOWED|biological

The output should look like :
{
    "entities": [{"label":"Authority","id":string,"Abbreviation":string}],
    "relationships": ["Authority|SUPPORT|Approach"]
}

"""

# for page in np.arange(3,10):
with open("texts/output_4.txt", "r", encoding="ascii") as f:
    text = f.readlines()
    text = " ".join(text)
    text = text.replace("/n", "")
    stream = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": system_promt},
            {"role": "user", "content": user_promt},
        ],
        stream=True,
    )

    for chunk in stream:
        print(chunk["message"]["content"], end="", flush=True)
