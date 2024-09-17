import { useState, useEffect } from 'react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import { MainContainer, ChatContainer, MessageList, Message, MessageInput, TypingIndicator, Sidebar } from '@chatscope/chat-ui-kit-react';
import './App.css';
import NavBar from './Components/NavBar';
import GraphComponent from './Components/GraphComp';

const backendUrl = "http://localhost:5001";
console.log("This is backend URL", backendUrl);

function App() {
  const [typing, setTyping] = useState(false);
  const [selectedNodes, setSelectedNodes] = useState([])
  const [graphs, setGraphs] = useState([
    {nodes: [], edges: []}
  ])

  const [selectedGraph, setSelectedGraph] = useState(graphs[graphs.length-1]);
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

    setSelectedGraph(subGraph_new);
    const newGraphs = [...graphs, subGraph_new]; 

    setGraphs(newGraphs);
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
      for (const node in selectedGraph.nodes){
        if (nodes_string.slice(1,nodes_string.length-1) === selectedGraph.nodes[node].id){
          const newSelectedNodes = [...selectedNodes, selectedGraph.nodes[node]];
          setSelectedNodes(newSelectedNodes);
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
