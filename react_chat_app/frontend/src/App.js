import { useState, useEffect } from 'react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import { MainContainer, ChatContainer, MessageList, Message, MessageInput, TypingIndicator, Sidebar } from '@chatscope/chat-ui-kit-react';
import './App.css';
import NavBar from './Components/NavBar';
import GraphComponent from './Components/GraphComp';
import Graph from 'react-graph-vis'
// const backendUrl = process.env.REACT_APP_BACKEND_URL;

// const backendUrl = process.env.REACT_APP_BACKEND_SERVER
const backendUrl = "http://localhost:5001"
console.log("This is backend URL", backendUrl)

// function processingSubgraph(subgraphData){
//   let nodes = []
//   let nodes_object = {}
//   let edges = []
//   let edges_object = {}
//   const color_dictionary = {
//     "__Entity__" : "#e04141",
//     "__Chunk__" : "yellow"
//   }
//   // alert(Object(subgraphData[0].keys()))
//   // alert(subgraphData[0].length)
//   // alert(Object.keys(subgraphData[0][0]))
//   // alert(Object.keys(subgraphData[0][1]))
//   // let count = 0;
//   let node_keeper = [];
//   let count = 0;
//   for (let i = 0; i < subgraphData.length; i++){
//     const record = subgraphData[i];
//     const node = record[0];
//     const neighbors = record[1];

//     const node_id = node['name'];
//     if (node_id == null){
//       alert("node is null");
//     }

//     const node_properties = JSON.stringify(node['properties']);
//     if( !node_keeper.includes(node_id) ){
//       let color_label = "red";
//       for (let key in color_dictionary) {
//         if (color_dictionary.hasOwnProperty(key)) {
//             // Check if the key exists in node["labels"]
//             if (node.labels.includes(key)) {
//                 color_label = color_dictionary[key];
//                 break;  // Exit the loop once a match is found
//             }
//         }
//       }
//       const node_ = {id: node_id, label: node_id, color: color_label, properties: node_properties}
//       nodes.push(node_);
//       nodes_object["id"] = node_;
//       node_keeper.push(node_id);
//       count += 1;
//     }

//     for (let j = 0; j < neighbors.length; j++){
//       let neighbor_info = neighbors[j];

//       let neighbor = neighbor_info['neighbor'];
//       let relationship = neighbor_info['relationship'];
//       if (neighbor){
//         let neighbor_id = neighbor['name'];
//         if (neighbor_id == null){
//           alert("neighbor node is null");
//         }
//         let neighbor_properties = JSON.stringify(neighbor['properties']);
//         if ( !node_keeper.includes(neighbor_id)){

//           let color_label = "red";
//           for (let key in color_dictionary) {
//             if (color_dictionary.hasOwnProperty(key)) {
//                 // Check if the key exists in node["labels"]
//                 if (neighbor.labels.includes(key)) {
//                     color_label = color_dictionary[key];
//                     break;  // Exit the loop once a match is found
//                 }
//             }
//           }
//           const node_ = {id: neighbor_id, label: neighbor_id, color: color_label, properties: neighbor_properties};
//           nodes.push(node_);
//           nodes_object["id"] = node_;
//           node_keeper.push(neighbor_id);
//           count += 1;
//         }
//         if (relationship){
//           let relationship_label = relationship["label"] ;
//           let relationship_property = relationship['properties'];
//           edges.push({from: node_id, to: neighbor_id});
//         }
//       }
//     }
//   }
//   return [nodes, edges, nodes_object, edges_object]
// }


function App() {
  const [typing, setTyping] = useState(false);
  const [selectedNodes, setSelectedNodes] = useState([])
  const [graphs, setGraphs] = useState([
    {nodes: [], edges: []}
  ])
  const [graphsRaw, setGraphsRaw] = useState([
    {nodes: {}, edges: {}}
  ])

  const [subGraphNew, setSubGraphNew] = useState({nodes: [], edges: []})

  const [selectedGraph, setSelectedGraph] = useState(graphs[graphs.length-1]);
  // const [graph, setGraph] = useState(
  //   {nodes: [], edges: []}
  // );
  // const [selectedGraphRaw, setSelectedGraphRaw] = useState(graphsRaw[graphsRaw.length - 1]);
  const [messages, setMessages] = useState([
    {
      message: 'Hello, I am KGB. How am I at your service?',
      sender: "ChatGPT",
      direction: "incoming"
    }
  ]);

  const color_dictionary = {
    "__Chunk__" : "yellow",
    "__Entity__" : "#e04141",
    "__Community__": "blue"
  }

  const handleSend = async (message) => {
    const newMessage = {
      message: message,
      sender: "user",
      direction: "outgoing"
    };

    const newMessages = [...messages, newMessage];

    // update our messages state
    setMessages(newMessages);
    // process message to chatGPT (send it over and wait for response)
    setTyping(true);

    await processAnswer(newMessages, message);
  };

  const handleGraphClick = (graph) => {
    setSelectedGraph(graph); // Update the selected graph
  };

  async function processAnswer(messages, userQuery) {
    // const response = await fetch(`${backendUrl}/get_answer_neo4j`, {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({ question: userQuery })
    // });
    // const data = await response.json();

    // const { contexts, chunkIds, scores } = data;

    // const local_retriever = await fetch(`${backendUrl}/local_retriever`, {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({ question: userQuery })
    // });

    // const local_retriever_data = await local_retriever.json();

    // const local_text_chunk_ids = local_retriever_data[0]["text_mapping"];

    // setLocalTextChunkIds(local_text_chunk_ids);

    // const local_summary_ids = local_retriever_data[0]["report_mapping"];

    // setLocalSummaryIds(local_summary_ids);

    // const global_retriever = await fetch(`${backendUrl}/global_retriever`, {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({ question: userQuery })
    // });

    // const global_retriever_data = await global_retriever.json();

    // setGlobalSummaryIds(global_retriever_data);


    // let graph = {nodes: [], edges: []}
    // if (local_text_chunk_ids.length > 0 || local_summary_ids.length > 0 || global_retriever_data.length > 0){
    //   const graph_temp = await fetch(`${backendUrl}/get_subgraph`, {
    //     method: 'POST',
    //     headers: {
    //       'Content-Type': 'application/json'
    //     },
    //     body: JSON.stringify({ "local_text_chunk_ids": localTextChunkIds, "local_summary_ids": localSummaryIds, "global_summary_ids": globalSummaryIds  })
    //   });
    //   const graph_temp_data = await graph_temp.json();
    //   graph = graph_temp_data;
    //   alert(graph_temp_data["nodes"]);
    //   alert(graph_temp_data["edges"]);
    //   setSelectedGraph(graph);
    // }

    // const subgraphResponse = await fetch(`${backendUrl}/query_subgraph`, {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({ chunkIds })
    // });
    // const subgraphData = await subgraphResponse.json();

    // const [nodes, edges, nodes_object, edges_object] = processingSubgraph(subgraphData);

    const get_subgraph_response = await fetch(`${backendUrl}/get_subgraph`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ question: userQuery })
    })

    const {subGraph_new, contexts} = await get_subgraph_response.json();

    // Iterate through nodes and assign colors
    subGraph_new.nodes.forEach(node => {
      for (const [label, color] of Object.entries(color_dictionary)) {
          if (node.type.includes(label)) {
              node.color = color;
              break;
          }
      }
    });
    // setSubGraphNew(subGraph_new);

    // const graph = {nodes: nodes, edges: edges};
    // const graphRaw = {nodes: nodes_object, edges: edges_object};
    setSelectedGraph(subGraph_new);
    // setSelectedGraphRaw(graphRaw);
    const newGraphs = [...graphs, subGraph_new];

    // const graph = {nodes: nodes, edges: edges};
    // // const graphRaw = {nodes: nodes_object, edges: edges_object};
    // setSelectedGraph(graph);
    // // setSelectedGraphRaw(graphRaw);
    // const newGraphs = [...graphs, graph];
    setGraphs(newGraphs);
    // setGraphsRaw()

    // setGraph(graph)

    // const secondaryNodesResponse = await fetch(`${backendUrl}/query_secondary_nodes`, {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({ primaryNodes: chunkIds })
    // });
    // const secondaryNodesData = await secondaryNodesResponse.json();

    // const appearedInNodesResponse = await fetch(`${backendUrl}/query_appeared_in_nodes`, {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({ secondaryNodes: secondaryNodesData })
    // });
    // const appearedInNodesData = await appearedInNodesResponse.json();

    // const responseMessage = `Contexts: ${contexts.join(', ')}\nSubgraph: ${JSON.stringify(subgraphData)}\nSecondary Nodes: ${JSON.stringify(secondaryNodesData)}\nAppeared In Nodes: ${JSON.stringify(appearedInNodesData)}`;
    const responseMessage_contents = `${contexts['contents'].join(', ')}`;
    const responseMessage_summaries = `${contexts['summaries'].join(', ')}`;

    let chat_history = messages.map(msg => `${msg.sender}: ${msg.message}`).join("\n");

    const response_openai = await fetch(`${backendUrl}/get_response`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_query: userQuery,  // Fixed to match the Python key
        contents: responseMessage_contents,
        summaries: responseMessage_summaries,
        chat_history: chat_history
      })
    });

    const responseData = await response_openai.json();

    const newMessages = [
      ...messages,
      {
        message: responseData["answer"],
        sender: "ChatGPT",
        direction: "incoming"
      }
    ];

    setMessages(newMessages);
    setTyping(false);
  }

  const events = {
    selectNode: ({nodes}) => {

      let nodes_string = JSON.stringify(nodes[0]);
      // alert(nodes_string.slice(1,nodes_string.length-1));
      // alert(typeof nodes_string === 'string');
      for (const node in selectedGraph.nodes){
        // if (node < 1){
        //   alert(selectedGraph.nodes[node].id);
        //   alert(typeof selectedGraph.nodes[node].id === 'string');
        // }
        if (nodes_string.slice(1,nodes_string.length-1) === selectedGraph.nodes[node].id){
          const newSelectedNodes = [...selectedNodes, selectedGraph.nodes[node]];
          setSelectedNodes(newSelectedNodes);
          // alert("Found it!");
          // alert(selectedNodes.length);
          break;
        }
      }
    }
  }

  return (
    <div className='App'>
      <NavBar style={{position: 'absolute'}} title={'KGB_TruthGuiding'}/>
      <div style={{display: 'flex'}}>
        <div style={{ position: 'relative', height:'900px', width: '1500px'}}>
          <MainContainer >
            <Sidebar style={{ height: '900px', width: "300px"}} position='left'>
              <h2>Sidebar</h2>
              <p>Chat history in graph</p>
              <ul>
                {graphs.map((graph, i) => {
                  return <li
                    key={i}
                    onClick={() => handleGraphClick(graph)}
                    style={{
                      color: 'blue',
                      textDecoration: 'underline',
                      cursor: 'pointer',
                      marginBottom: '10px' // optional, to add spacing between items
                    }}
                    >
                      Graph {i}
                  </li>
                })}
              </ul>

              <button
                onClick={() => {
                  // Clear the selectedNodes array
                  setSelectedNodes([]);
                }}
                style={{
                  padding: '10px 20px',
                  backgroundColor: 'pink',
                  color: 'white',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  alignSelf: 'center',
                  marginBottom: '20px'
                }}
              >
                Delete Selected Nodes
              </button>
            </Sidebar>
            <div>
              <h2>Chat Window</h2>
              <ChatContainer >
                <MessageList typingIndicator={typing ? <TypingIndicator content="Typing ..."/> : null}>
                  {messages.map((message, i) => {
                    return <Message key={i} model={message} />
                  })}
                </MessageList>
                <MessageInput placeholder='Type message here' onSend={handleSend} />
              </ChatContainer>
            </div>
          </MainContainer>
        </div>

        <GraphComponent selectedGraph={selectedGraph} events={events} selectedNodes={selectedNodes}/>
      </div>
    </div>

  );
}

export default App;
