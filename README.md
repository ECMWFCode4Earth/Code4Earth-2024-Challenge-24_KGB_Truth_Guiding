# Knowledge Graph Generation for Enhanced Chatbot and Scientific Literature Synthesis - Code4Earth challenge 24
The aim of the project is to create a knowledge graph for Scientific documents. This is linked directly to the challenge https://github.com/ECMWFCode4Earth/challenges_2024/issues/7


## Overview
The project aims to enhance the user experiences of ECMWF’s experimental AI-based assistant. ECMWF chatbox based on GPT provides users with an intuitive and easy-to-use self-service chat-like interface to get their questions answered without the need to contact the dedicated support services. The application of GPT can generate human-like answers. However, like almost all other LLMs, their responses are not always reliable.

The construction of a knowledge graph and its integration into the chatbot is promising to improve the reliability of this conversational assistant’s responses. Besides, a tool that generates interactive graphs can help users summarise the idea behind the answers. Additionally, knowledge graphs can also help beginners to easily catch the scientific terms, ideas, and an overview of the domain.

In detail, the knowledge graphs will be constructed from various datasets, including scientific literature, weather data, domain-specific ontologies, etc. 

In the end, this project will provide the ECMWF chatbot with a knowledge graph database.

## Features

List the main features and functionalities of the Knowledge Graph:

- Feature 1: Description
- Feature 2: Description
- ...

## Installation

To install necessary packages run:

```
pip install -r requirements.txt
```

### Neo4j :

We highly recommend you to use Neo4j Desktop if it is available for you due to its simplicity and UI interactions.

Installing Neo4j Desktop is fairly easy. You can follow this link to download and install it :
https://neo4j.com/docs/desktop-manual/current/installation/

Once Neo4j is installed, you can set up your own new local database as following :
- First, open Neo4j Desktop
- Click on Projects, then New (the field with a + symbol) to create a new project
- Then, on your project, click on button **Add** and select **Local DBMS**, set up the name and password as you like, and finally click on **Create** to create the database
- Each time that you want to run the app and/or work on the database, don't forget to start the database first by clicking (or hovering) on the database, and click **Start**

To run and use the app, you will need to install certain plugins of Neo4j :

#### APOC
More details here : https://neo4j.com/labs/apoc/4.1/installation/

But, in brief, you can do as follow :

- APOC Core : APOC Core can be installed by moving the APOC jar file from the $NEO4J_HOME/labs directory to the $NEO4J_HOME/plugins directory and restarting Neo4j.
- Neo4j Desktop : APOC Full can be installed with Neo4j Desktop, after creating your database, by going to the Manage screen, and then the Plugins tab. Click Install in the APOC box and wait until you see the "Installed" message.

#### Graph-Data-Science

More details here : https://neo4j.com/docs/graph-data-science/current/installation/

Similar to APOC, you have several ways to install the library Graph-Data-Science :

- If you use Neo4j Desktop, you can install it from the UI, similarly to APOC
- If you run Neo4j in a Docker container, you need to configure the GDS library as a Neo4j Docker plugin
- If you use Neo4j Server (Community or Enterprise), you need to install the GDS library manually. Please follow the link above for more details !

## Usage

Explain how to use the Knowledge Graph, including any specific commands, APIs, or interfaces available.

## Data Sources

List the sources of data used to populate the Knowledge Graph, including any APIs, databases, or external datasets.

## Architecture

Describe the architecture of the Knowledge Graph, including the technology stack used, data modeling approach, and any frameworks or libraries employed.

## Examples

Provide examples or use cases demonstrating how the Knowledge Graph can be queried or utilized to extract insights or perform analysis.

## Contributors

List the contributors to the project, along with their roles or contributions.

## License

Specify the license under which the project is released. Choose an appropriate open-source license (e.g., MIT, Apache) and include the license text.

## Acknowledgements

Acknowledge any individuals, organizations, or resources that contributed to the project or provided support and guidance.
