# Knowledge Graph Generation for Enhanced Chatbot and Scientific Literature Synthesis - Code4Earth challenge 24
The aim of the project is to create a knowledge graph for Scientific documents. This is linked directly to the challenge https://github.com/ECMWFCode4Earth/challenges_2024/issues/7



## Overview


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

## Usage

To use, please create an `.env` file in the outer folder and add the following variables:

- `OPENAI_API_KEY`=<YOUR_OPENAI_API_KEY>
- `KGGENRATOR`="8080"

Add your documents (type `txt`) in the txt_files

then run: `docker-compose up --build`

To use the interface, wait until the service `neo4j-uploader` exits succesfully.

Then go to `http://localhost:3000`

and type you question.

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
