from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
# from neo4j_queries import get_answer_neo4j, query_subgraph, get_response, query_secondary_nodes, query_appeared_in_nodes, local_retriever, global_retriever, get_subgraph
from neo4j_queries import get_answer_neo4j, get_response, local_retriever, global_retriever, get_subgraph
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

@app.route('/get_response', methods=['POST'])
def get_response_route():
    data = request.json
    # print("Here in the route", file=sys.stdout)
    user_query = data['user_query']
    contents = data['contents']
    summaries = data['summaries']
    chat_history = data['chat_history']
    answer = get_response(user_query, contents,summaries, chat_history)
    return jsonify({"answer": answer})

# @app.route('/query_subgraph', methods=['POST'])
# def query_subgraph_route():
#     data = request.json
#     chunkIds = data['chunkIds']
#     records = query_subgraph(chunkIds)
#     return jsonify(records)

# Define route for the local retriever
@app.route('/local_retriever', methods=['POST'])
def local_retriever_route():
    data = request.json  # Get the JSON data from the request
    question = data['question']  # Extract the question parameter
    print("In the local retriever", file=sys.stdout)
    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Call the local_retriever function
    try:
        result = local_retriever(question)
        print("In the local retriever 2", file=sys.stdout)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Define route for the global retriever
@app.route('/global_retriever', methods=['POST'])
def global_retriever_route():
    data = request.json  # Get the JSON data from the request
    question = data['question']  # Extract the question parameter
    
    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Call the global_retriever function
    try:
        result = global_retriever(question)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_subgraph', methods=['POST'])
def get_subgraph_route():
    data = request.json
    question = data["question"]
    if not question:
        return jsonify({"error": "Question is required"}), 400
    try:
        graph, contexts = get_subgraph(question)
        # print(f"Inside get subgraph route {graph['edges']}",file=sys.stdout)
        return jsonify({"subGraph_new": graph, "contexts": contexts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route('/query_secondary_nodes', methods=['POST'])
# def query_secondary_nodes_route():
#     data = request.json
#     primaryNodes = data['primaryNodes']
#     secondary_nodes = query_secondary_nodes(primaryNodes)
#     return jsonify(secondary_nodes)

# @app.route('/query_appeared_in_nodes', methods=['POST'])
# def query_appeared_in_nodes_route():
#     data = request.json
#     secondaryNodes = data['secondaryNodes']
#     appeared_in_nodes = query_appeared_in_nodes(secondaryNodes)
#     return jsonify(appeared_in_nodes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
