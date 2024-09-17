import "./NavBar.css"
import Popup from 'reactjs-popup';
import 'reactjs-popup/dist/index.css';
import LocalRetriever from '../media/Local_Retriever.png';
import GlobalRetriever from '../media/Global_Retriever.png'

function NavBar ({title}) {
    return (
        <nav className="NavBar">
            <div className="Center">
                <h1>{title}</h1>
            </div>

            <div className="Right">
                <a href="https://github.com/Viet1004/Code4Earth-2024-Challenge-24">Source Code</a>
            </div>
            <Popup trigger={<button> Our approach </button>}>
                <div>
                  Our approach is based on the paper GraphRAG of Microsoft.
                  The database is organised into three type of nodes:
                  <ul>
                    <li><b>Entity:</b> Extracted from text</li>
                    <li><b>Chunk:</b> Divided from document. Entities are extracted from chunks.</li>
                    <li><b>Community:</b> Clustered from entities. It generate more global knowledge.</li>
                  </ul>
                  For more information on how to construct database, please refer to our repository.
                  We describe here the retrieval mechanism to collect context so that LLM can answer user's question.
                  
                  <h2>Retrieval mechanism</h2>
                  Two mechanisms:
                  <h3>Local retrieval</h3> 
                  <img src={LocalRetriever} width="400px"></img>
                  <p>Based on the vector similarity with the (natural language) query from users, the most similar entities are collected. 
                  Then, text chunks with the most connected entities (above) are selected. Similarly, communities with the most ranking are collected. (Ranking is based on the degree of community node)
                  The content of text chunk and the summary in community nodes and the name of entities are used for contexts for LLM.
                  </p>
                  <h3>Global retrieval</h3>
                  <img src={GlobalRetriever} width="400px"></img>
                  <p>Based on the vector similarity with the (natural language) query from users, collect the most similar communities which will be used for contexts for LLM.</p>
                
                </div>

              </Popup>
        </nav>
    )
}

export default NavBar;