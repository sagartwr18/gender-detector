import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import CameraFeed from "./components/CameraFeed"
import GenderInfo from "./components/GenderInfo"
import kivasLogo from "./assets/Kivas Logo.jpeg"
import "./App.css"

function App() {
  const [detectedGender, setDetectedGender] = useState(null);
  const [infoKey, setInfoKey] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  
  const cameraFeedRef = useRef(null);
  const genderInfoRef = useRef(null);

  const handleGenderDetected = (gender) => {
    if (isAnimating || detectedGender) return;
    
    setIsAnimating(true);
    setDetectedGender(gender);
    setInfoKey(prev => prev + 1);
  };

  // Animate when detectedGender changes
  useEffect(() => {
    if (detectedGender && cameraFeedRef.current && genderInfoRef.current) {
      // Initial state: GenderInfo is below the screen
      gsap.set(genderInfoRef.current, { y: "100%", opacity: 1 });
      
      // Animate CameraFeed swipe up
      gsap.to(cameraFeedRef.current, {
        y: "-100%",
        duration: 0.7,
        ease: "power3.inOut",
        onComplete: () => {
          // Animate GenderInfo up from bottom
          gsap.to(genderInfoRef.current, {
            y: "0%",
            duration: 0.7,
            ease: "power3.out",
            onComplete: () => setIsAnimating(false)
          });
        }
      });
    }
  }, [detectedGender]);

  const handleRestart = () => {
    if (isAnimating) return;
    
    setIsAnimating(true);
    
    // Animate GenderInfo down (swipe out)
    gsap.to(genderInfoRef.current, {
      y: "100%",
      duration: 0.6,
      ease: "power3.inOut",
      onComplete: () => {
        // Bring CameraFeed back
        gsap.to(cameraFeedRef.current, {
          y: "0%",
          duration: 0.6,
          ease: "power3.out",
          onComplete: () => {
            setDetectedGender(null);
            setInfoKey(prev => prev + 1);
            setIsAnimating(false);
          }
        });
      }
    });
  };

  return (
    <div className="app">
      
      <nav className="navbar">
        <div className="navbar-logo">
          <img src={kivasLogo} alt="KIVAS TECH Logo" className="logo-image"/>
          <span className="navbar-brand">KIVAS TECH</span>
        </div>
      </nav>
      
      <main className="main-content">
        {/* Camera Feed Layer - Always rendered */}
        <div 
          ref={cameraFeedRef} 
          className="transition-layer"
        >
          <CameraFeed onGenderDetected={handleGenderDetected} />
        </div>
        
        {/* Gender Info Layer - Always rendered but initially hidden */}
        <div 
          ref={genderInfoRef} 
          className="transition-layer"
          style={{ transform: "translateY(100%)" }}
        >
          <GenderInfo 
            gender={detectedGender} 
            keyVal={infoKey} 
            onRestart={handleRestart}
          />
        </div>
      </main>

    </div>
  )
}

export default App
