'use client';
import { useEffect, useState } from "react";
import "./CameraFeed.css";

function CameraFeed({ onGenderDetected, onCameraState }) {
  const [state, setState] = useState("camera");

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://127.0.0.1:8000/state")
        .then(res => res.json())
        .then(data => {
          const normalizedState = String(data?.state ?? "").toLowerCase();

          if (!normalizedState) return;

          setState(prevState => {
            if (prevState === normalizedState) return prevState;

            if (normalizedState === "male" || normalizedState === "female") {
              onGenderDetected?.(normalizedState);
            } else if (normalizedState === "camera") {
              onCameraState?.();
            }

            return normalizedState;
          });
        })
        .catch(err => console.log(err));
    }, 1000);

    return () => clearInterval(interval);
  }, [onGenderDetected, onCameraState]);

  return (
    <div className="camera-page">
      <div className="camera-card">
        <div className="video-section">
          <div className="scan-line" />
          <div className="live-badge">
            <span className="live-dot" />
            <span className="live-label">LIVE</span>
          </div>
          <img src="http://127.0.0.1:8000/video" alt="Camera feed" className="frame-image" />
        </div>
      </div>
    </div>
  );
}

export default CameraFeed;
