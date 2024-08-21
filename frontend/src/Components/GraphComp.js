import React, { useEffect, useState } from 'react';
import Graph from 'react-graph-vis';

const GraphComponent = ({ selectedGraph, events, selectedNodes}) => {
  const [graphHeight, setGraphHeight] = useState(window.innerHeight * 0.6); // 60% of the screen height

  useEffect(() => {
    const handleResize = () => {
      setGraphHeight(window.innerHeight * 0.6); // Adjust the graph height on window resize
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '1200px' }}>
      {/* Graph Window */}
      <div style={{
        height: `${graphHeight}px`, // Dynamically set height based on screen size
        border: '0.8px solid lightgrey',
        marginBottom: '10px',
        padding: '0', // Ensure no extra padding is causing overflow
        boxSizing: 'border-box',
        overflow: 'hidden', // Prevents the graph from exceeding its container
        
      }}>
        <h1 style={{ margin: '0', padding: '10px', boxSizing: 'border-box' }}>Graph</h1>
        <Graph
          style={{ height: 'calc(100% - 20px)', width: '100%' }} // Adjust to account for header height
          graph={selectedGraph}
          events={events}
        />
      </div>

      {/* Side Information Window */}
      <div style={{
        flex: 1,
        border: '0.8px solid lightgrey',
        padding: '10px',
        boxSizing: 'border-box',
        
      }}>
        <h1>Node information</h1>
            <ul>
                {selectedNodes.map((node, i) =>{
                    return (
                        <li>
                            {node['id']}
                            {node['properties']}
                        </li>
                    )
                })}
            </ul>
        {/* Add your side information content here */}
      </div>
    </div>
  );
};

export default GraphComponent;
