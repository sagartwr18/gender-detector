'use client';
import { useEffect, useState } from "react";
import * as React from 'react';
import {
  Sun,
  Glasses,
  Camera,
  ScanFace,
} from 'lucide-react';
import "./CameraFeed.css";

const INSTRUCTIONS = [
  { icon: <ScanFace size={15} strokeWidth={1.8} />,  text: "Position your face in the center of the frame" },
  { icon: <Sun      size={15} strokeWidth={1.8} />,  text: "Ensure good lighting on your face" },
  { icon: <Glasses  size={15} strokeWidth={1.8} />,  text: "Remove glasses or hats for better accuracy" },
  { icon: <Camera   size={15} strokeWidth={1.8} />,  text: "Look directly at the camera" },
];

function CameraFeed({ onGenderDetected }) {
  const [state, setState] = useState("camera");

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://127.0.0.1:8000/state")
        .then(res => res.json())
        .then(data => {
          if (data.state === "male" || data.state === "female") {
            if (state !== data.state) {
              setState(data.state);
              // Call the callback with the detected gender
              if (onGenderDetected) {
                onGenderDetected(data.state);
              }
            }
          } else {
            setState(data.state);
          }
        })
        .catch(err => console.log(err));
    }, 1000);
    return () => clearInterval(interval);
  }, [state, onGenderDetected]);

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
        <div className="info-section">
          <h3 className="info-title">Instructions</h3>
          <ul className="instructions-list">
            {INSTRUCTIONS.map((item, i) => (
              <li key={i}>
                <span className="li-icon">{item.icon}</span>
                {item.text}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default CameraFeed;
