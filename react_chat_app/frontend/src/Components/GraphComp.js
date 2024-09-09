import React, { useEffect, useState } from 'react';
import Graph from 'react-graph-vis';
import "./GraphComp.css"

const GraphComponent = ({ selectedGraph, events, selectedNodes }) => {
  const [graphHeight, setGraphHeight] = useState(window.innerHeight * 0.6); // 60% of the screen height
  const fixedWidth = '800px'; // Fixed width for both windows

  const color_dictionary = {
    "__Entity__": "#e04141",
    "__Chunk__": "yellow",
    "__Community__": "blue"
  };

  // Select all divs with the class 'colored-div'
  document.querySelectorAll('.colored-div').forEach(function(div) {
      // Get the entity type from the data attribute
      const entityType = div.getAttribute('data-entity');
      // Check if the entity type is in the color dictionary
      if (color_dictionary[entityType]) {
          // Apply the color from the dictionary
          div.style.backgroundColor = color_dictionary[entityType];
      }
  });


  useEffect(() => {
    const handleResize = () => {
      setGraphHeight(window.innerHeight * 0.6); // Adjust the graph height on window resize
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', width: fixedWidth }}>
      {/* Graph Window */}
      <div style={{
        height: `${graphHeight}px`, // Dynamically set height based on screen size
        width: fixedWidth, // Fixed width
        border: '0.8px solid lightgrey',
        marginBottom: '10px',
        padding: '0', // Ensure no extra padding is causing overflow
        boxSizing: 'border-box',
        overflow: 'hidden', // Prevents the graph from exceeding its container
        flexShrink: 0, // Prevent the graph window from resizing
      }}>
        <h1 style={{ margin: '0', padding: '10px', boxSizing: 'border-box' }}>Graph</h1>
        <Graph
          style={{ height: 'calc(100% - 20px)', width: '100%' }} // Adjust to account for header height
          graph={selectedGraph}
          events={events}
        />
      </div>
      <div>
      <div data-entity="__Entity__">This is an Entity</div>
        <div data-entity="__Chunk__">This is a Chunk</div>
        <div data-entity="__Community__">This is a Community</div>
      </div>
      {/* Side Information Window */}
      <div style={{
        height: '300px', // Fixed height for the side information window
        width: fixedWidth, // Fixed width
        border: '0.8px solid lightgrey',
        padding: '10px',
        boxSizing: 'border-box',
        overflowY: 'auto', // Allow scrolling if content exceeds height
      }}>
        <h1>Node Information</h1>
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          {selectedNodes.map((node, i) => {
            // Determine the type and content of the node based on its properties
            let type, content;

            if (node.properties.level) {
              type = "Community";
              content = node.properties.summary ? node.properties.summary : "";
            } else if (node.properties.content) {
              type = "Chunk";
              content = node.properties.content;
            } else if (node.properties.name) {
              type = "Entity";
              content = node.properties.name;
            } else {
              // Fallback for nodes without the specific properties
              type = "Unknown";
              content = JSON.stringify(node.properties, null, 2);
            }

            return (
              <li
                key={i}
                style={{
                  wordWrap: 'break-word',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                <strong>ID:</strong> {node.id}
                <br />
                <strong>Type:</strong> {type}
                <br />
                <strong>Content:</strong> {content}
                <p>==============================</p>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
};

export default GraphComponent;
