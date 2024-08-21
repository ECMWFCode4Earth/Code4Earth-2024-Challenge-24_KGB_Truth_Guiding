import { useState } from 'react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import { MainContainer, ChatContainer, MessageList, Message, MessageInput, TypingIndicator, Sidebar } from '@chatscope/chat-ui-kit-react';
import './App.css';
import NavBar from './Components/NavBar';
import GraphComponent from './Components/GraphComp';
import Graph from 'react-graph-vis'
// const backendUrl = process.env.REACT_APP_BACKEND_URL;

const backendUrl = "http://localhost:5000"

console.log("This is backend URL", backendUrl)

function processingSubgraph(subgraphData){
  let nodes = []
  let nodes_object = {}
  let edges = []
  let edges_object = {}
  let color_label = {
    "entity" : "#e04141",
    "chunk" : "yellow"
  }
  // alert(Object(subgraphData[0].keys()))
  // alert(subgraphData[0].length)
  // alert(Object.keys(subgraphData[0][0]))
  // alert(Object.keys(subgraphData[0][1]))
  // let count = 0;
  let node_keeper = [];
  let count = 0;
  for (let i = 0; i < subgraphData.length; i++){
    const record = subgraphData[i];
    const node = record[0];
    const neighbors = record[1];

    const node_id = node['name'];
    if (node_id == null){
      alert("node is null");
    }
    const node_properties = node['properties'];
    if( !node_keeper.includes(node_id) ){
      const node = {id: node_id, label: node_id, color: color_label["entity"], properties: node_properties}
      nodes.push(node);
      nodes_object["id"] = node; 
      node_keeper.push(node_id);
      count += 1;
    }
    
    for (let j = 0; j < neighbors.length; j++){
      let neighbor_info = neighbors[j];

      let neighbor = neighbor_info['neighbor'];
      let relationship = neighbor_info['relationship'];
      if (neighbor){
        let neighbor_id = neighbor['name'];
        if (neighbor_id == null){
          alert("neighbor node is null");
        }
        let neighbor_properties = neighbor['properties'];  
        if ( !node_keeper.includes(neighbor_id)){
          const node = {id: neighbor_id, label: neighbor_id, color: color_label["entity"], properties: neighbor_properties}; 
          nodes.push(node);
          nodes_object["id"] = node;
          node_keeper.push(neighbor_id);
          count += 1;
        }
        
        if (relationship){
          let relationship_label = relationship["label"] ;
          let relationship_property = relationship['properties'];  
          edges.push({from: node_id, to: neighbor_id}); 
        }
      }
    }
  }
  return [nodes, edges, nodes_object, edges_object]
}


function App() {
  const [typing, setTyping] = useState(false);
  const [selectedNodes, setSelectedNodes] = useState([])
  const [graphs, setGraphs] = useState([
    {nodes: [], edges: []}
  ])
  const [graphsRaw, setGraphsRaw] = useState([
    {nodes: {}, edges: {}}
  ])
  
  const [selectedGraph, setSelectedGraph] = useState(graphs[graphs.length-1]);
  // const [graph, setGraph] = useState(
  //   {nodes: [], edges: []}
  // );
  const [selectedGraphRaw, setSelectedGraphRaw] = useState(graphsRaw[graphsRaw.length - 1]);
  const [messages, setMessages] = useState([
    {
      message: 'Hello, I am KGB. How am I at your service?',
      sender: "ChatGPT",
      direction: "incoming"
    }
  ]);

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
    const response = await fetch(`${backendUrl}/get_answer_neo4j`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ question: userQuery })
    });
    const data = await response.json();

    const { contexts, chunkIds, scores } = data;

    const subgraphResponse = await fetch(`${backendUrl}/query_subgraph`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ chunkIds })
    });
    const subgraphData = await subgraphResponse.json();

    const [nodes, edges, nodes_object, edges_object] = processingSubgraph(subgraphData);

    const graph = {nodes: nodes, edges: edges};
    // const graphRaw = {nodes: nodes_object, edges: edges_object};
    setSelectedGraph(graph);
    // setSelectedGraphRaw(graphRaw);
    const newGraphs = [...graphs, graph]; 
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
    const responseMessage = `Contexts: ${contexts.join(', ')}`;

    const newMessages = [
      ...messages,
      {
        message: responseMessage,
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
      alert(nodes_string.slice(1,nodes_string.length-1));
      alert(typeof nodes_string === 'string');
      for (const node in selectedGraph.nodes){
        if (node < 1){
          alert(selectedGraph.nodes[node].id);
          alert(typeof selectedGraph.nodes[node].id === 'string');
        }        
        if (nodes_string.slice(1,nodes_string.length-1) === selectedGraph.nodes[node].id){
          const newSelectedNodes = [...selectedNodes, selectedGraph.nodes[node]];
          setSelectedNodes(newSelectedNodes);
          alert("Found it!");
          alert(selectedNodes.length);
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
            <Sidebar style={{ height: '900px', overflow: 'hidden' }} position='left'>
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
            </Sidebar>
            <div>
              <h2>Chat Window</h2>
              <ChatContainer>
                <MessageList>
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
