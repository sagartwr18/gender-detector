import CameraFeed from "./components/CameraFeed"
import kivasLogo from "./assets/Kivas Logo.jpeg"
import "./App.css"

function App() {

  return (
    <div className="app">
      
      <nav className="navbar">
        <div className="navbar-logo">
          <img src={kivasLogo} alt="KIVAS TECH Logo" className="logo-image"/>
          <span className="navbar-brand">KIVAS TECH</span>
        </div>
      </nav>
      
      <main className="main-content">
        <CameraFeed />
      </main>

    </div>
  )
}

export default App