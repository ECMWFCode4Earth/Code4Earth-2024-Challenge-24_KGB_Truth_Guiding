# Knowledge Graph Generation for Enhanced Chatbot and Scientific Literature Synthesis - Code4Earth challenge 24
The aim of the project is to create a knowledge graph for Scientific documents. This is linked directly to the challenge https://github.com/ECMWFCode4Earth/challenges_2024/issues/7



## Overview
The project aims to enhance the user experiences of ECMWF's experimental AI-based assistant. ECMWF chatbox based on GPT provides users with an intuitive and easy-to-use self-service chat-like interface to get their questions answered without the need to contact the dedicated support services. The application of GPT can generate human-like answers. However, like almost all other LLMs, their responses are not reliable because of the hallucination phenomenon.\\
The construction of a knowledge graph and its integration into the chatbot 
is promising to improve the reliability of this conversational assistant's responses. Besides, a tool that generates interactive graphs can help users summarise the idea behind the answers. Additionally, knowledge graphs can also help beginners to easily catch the scientific terms, ideas, and an overview of the domain.\\
In detail, the knowledge graphs will be constructed from various datasets, including scientific literature, weather data, domain-specific ontologies, etc.

## Features

The outcome of the project is to create an app that user can add their source txt file into and start to chat with this.

List the main features and functionalities of the Knowledge Graph:

- Feature 0: Extracting information and generating database from this information.
- Feature 1: Partial implementation of GraphRAG (implemented by Microsoft). For this feature, from the database from feature 0, the system will retrieve both local and global information that is relevant to the query.
- Feature 2: Visualization of the retrieved information in feature 1.

## Installation

Install [docker](https://docs.docker.com/engine/install/)

## Usage

To use, please create an `.env` file in the outer folder and add the following variables:

- `OPENAI_API_KEY`=<YOUR_OPENAI_API_KEY>
- `KGGENRATOR`="8080"

Add your documents (type `txt`) in the txt_files

then run: `docker-compose build` to build images of services

Run the container by:
`docker-compose up`

In case of error when run each service, ensure that service kg_generator, neo4j_uploader exits successfully. Since `neo4j_uploader` requires service `neo4j` and `kg_generator`, ensure that it is the case.

Then go to `http://localhost:3000`

and type you question.

## Data Sources

The example is in the `source_pdf/` folder but to run, you need to insert txt files into the folder `tex_files/`

The application should work fine with `txt` files.

## Architecture

The applciation is composed of 5 services:

- `kg_generator`: Produce json file to push to neo4j database
- `neo4j`: Neo4j database with apoc and graphdatascience plugin installed.
- `neo4j_uploader`: Upload knowledge graph to neo4j database
- `flask_backend`: Flask backend.
- `frontend`: React frontend. 

For more information, consult the `.pptx` file

## Contributors


## License

GNU GENERAL PUBLIC LICENSE

## Acknowledgements

We would like to extend our gratitude to ECMWF organization for organizing `Code for earth challenge 24` and provide us with strong support from their experts.

Our work is greatly inspired by the paper: "From Local to Global: A Graph RAG Approach to Query-Focused Summarization".

The query to generate data structure (in `upload_db/graph_clustering.py`) is inspired by one series in [neo4j developer blog](https://neo4j.com/developer-blog/global-graphrag-neo4j-langchain/). 



