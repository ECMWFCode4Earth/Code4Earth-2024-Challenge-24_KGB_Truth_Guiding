import "./NavBar.css"

function NavBar ({title}) {
    return (
        <nav className="NavBar">
            <div className="Center">
                <h1>{title}</h1>
            </div>

            <div className="Right">
                <a href="https://github.com/Viet1004/Code4Earth-2024-Challenge-24">Source Code</a>
            </div>
        </nav>
    )
}

export default NavBar;