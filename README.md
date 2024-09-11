# Knowledge Graph Generation for Enhanced Chatbot and Scientific Literature Synthesis - Code4Earth challenge 24
The aim of the project is to create a knowledge graph for Scientific documents. This is linked directly to the challenge https://github.com/ECMWFCode4Earth/challenges_2024/issues/7



## Overview


## Features

List the main features and functionalities of the Knowledge Graph:

- Feature 0: Extracting information and generating database from this information.
- Feature 1: Partial implementation of GraphRAG (implemented by Microsoft). For this feature, from the database from feature 0, the system will retrieve both local and global information that is relevant to the query.
- Feature 2: Visualization of the retrieved information in feature 1.
  

## Installation

You don't need to install anything. The app will be run in containers.

## Usage

To use, please create an `.env` file in the outer folder and add the following variables:

- `OPENAI_API_KEY`=<YOUR_OPENAI_API_KEY>
- `KGGENRATOR`="8080"

Add your documents (type `txt`) in the txt_files

then run: `docker-compose build` to build images of services

To start container of each service run following commands in the order:

- `docker-compose up kg_generator`. This command start a service that looks for txt files in the `txt_files/` folder and outputs json files in the `assets/` folder. These json files presents `Nodes` and `Edges` generated from txt files.
- `docker-compose up neo4j`. This command is for starting neo4j databse and setup `URI`, `user`, `password` for the database.
- `docker-compose up neo4j_uploader`. This command starts a service which looks for json files in the `assets/` folder and push this to the neo4j database. At the same time, it define the structure of the database.
- `docker-compose up flask_backend`. This command starts backend service for web application.
- `docker-compose up frontend`. This command starts frontend service which communicate with flask_backend service.


Then go to `http://localhost:3000`

and type you question.

## Data Sources

List the sources of data used to populate the Knowledge Graph, including any APIs, databases, or external datasets.



## Architecture



## Contributors

List the contributors to the project, along with their roles or contributions.

## License

GNU GENERAL PUBLIC LICENSE

## Acknowledgements

We would like to extend our gratitude to ECMWF organization for organizing `Code for earth challenge 24` and provide us with strong support from their experts.
