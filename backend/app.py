from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from neo4j_queries import get_answer_neo4j, query_subgraph, query_secondary_nodes, query_appeared_in_nodes
import sys
app = Flask(__name__)
CORS(app)

load_dotenv()

@app.route('/get_answer_neo4j', methods=['POST'])
def get_answer_neo4j_route():
    data = request.json
    question = data['question']
    contexts, chunkIds, scores = get_answer_neo4j(question)
    return jsonify({"contexts": contexts, "chunkIds": chunkIds, "scores": scores})

@app.route('/query_subgraph', methods=['POST'])
def query_subgraph_route():
    data = request.json
    chunkIds = data['chunkIds']
    records = query_subgraph(chunkIds)

    return jsonify(records)

@app.route('/query_secondary_nodes', methods=['POST'])
def query_secondary_nodes_route():
    data = request.json
    primaryNodes = data['primaryNodes']
    secondary_nodes = query_secondary_nodes(primaryNodes)
    return jsonify(secondary_nodes)

@app.route('/query_appeared_in_nodes', methods=['POST'])
def query_appeared_in_nodes_route():
    data = request.json
    secondaryNodes = data['secondaryNodes']
    appeared_in_nodes = query_appeared_in_nodes(secondaryNodes)
    return jsonify(appeared_in_nodes)

if __name__ == '__main__':
    app.run(debug=True)
