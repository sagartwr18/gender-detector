'use client';
import { useEffect, useState, useRef } from "react";
import { motion, useInView } from 'framer-motion';
import * as React from 'react';
import {
  User,
  Sun,
  Glasses,
  Camera,
  ScanFace,
  CheckCircle2,
  ShieldCheck,
  Sparkles,
  Brain,
  HeartHandshake,
} from 'lucide-react';
import "./CameraFeed.css";

// ── Lucide icons are ~1.5KB each, zero extra deps ──

function TextFade({ direction, children, className = '', staggerChildren = 0.1 }) {
  const FADE_UP = {
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 80, damping: 18 } },
    hidden: { opacity: 0, y: direction === 'down' ? -14 : 14 },
  };
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });
  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={isInView ? 'show' : ''}
      variants={{ hidden: {}, show: { transition: { staggerChildren } } }}
      className={className}
    >
      {React.Children.map(children, (child) =>
        React.isValidElement(child)
          ? <motion.div variants={FADE_UP}>{child}</motion.div>
          : child
      )}
    </motion.div>
  );
}

const MALE_POINTS = [
  { icon: <ShieldCheck />,    text: "Confident posture and steady presence" },
  { icon: <ScanFace />,       text: "Clear facial features with calm expression" },
  { icon: <Brain />,          text: "Reflects strength and determination" },
  { icon: <CheckCircle2 />,   text: "Suitable for leadership and responsibility" },
];

const FEMALE_POINTS = [
  { icon: <Sparkles />,       text: "Graceful posture with confident appearance" },
  { icon: <ScanFace />,       text: "Calm and expressive facial features" },
  { icon: <HeartHandshake />, text: "Reflects warmth and resilience" },
  { icon: <Brain />,          text: "Shows creativity and leadership qualities" },
];

function ResultView({ gender, keyVal }) {
  const isMale  = gender === "male";
  const points  = isMale ? MALE_POINTS : FEMALE_POINTS;
  const desc    = isMale
    ? "A man appears confident and composed before the camera. His facial features are clear, reflecting strength, determination, and a steady presence."
    : "A woman appears confident and graceful before the camera. Her expression reflects calmness and intelligence, conveying warmth and resilience.";

  return (
    <div className="camera-page">
      <div className={`fullscreen-content ${isMale ? 'male-content' : 'female-content'}`} key={keyVal}>
        <TextFade direction="up" staggerChildren={0.11} className="fade-content">

          {/* Header */}
          <div className="result-header">
            <div className="result-icon-wrap">
              <User strokeWidth={2} />
            </div>
            <div className="result-header-text">
              <span className="result-label">Detection Result</span>
              <h2 className="result-title">{isMale ? "Male" : "Female"}</h2>
            </div>
          </div>

          {/* Body */}
          <div className="result-body">
            <p className="result-paragraph">{desc}</p>
            <ul className="result-points">
              {points.map((pt, i) => (
                <li key={i}>
                  <span className="check-icon">
                    {React.cloneElement(pt.icon, { strokeWidth: 2.2, size: 11 })}
                  </span>
                  {pt.text}
                </li>
              ))}
            </ul>
          </div>

        </TextFade>
      </div>
    </div>
  );
}

const INSTRUCTIONS = [
  { icon: <ScanFace size={15} strokeWidth={1.8} />,  text: "Position your face in the center of the frame" },
  { icon: <Sun      size={15} strokeWidth={1.8} />,  text: "Ensure good lighting on your face" },
  { icon: <Glasses  size={15} strokeWidth={1.8} />,  text: "Remove glasses or hats for better accuracy" },
  { icon: <Camera   size={15} strokeWidth={1.8} />,  text: "Look directly at the camera" },
];

function CameraFeed() {
  const [state, setState] = useState("camera");
  const [key,   setKey]   = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://127.0.0.1:8000/state")
        .then(res => res.json())
        .then(data => {
          if (data.state === "male" || data.state === "female") {
            if (state !== data.state) {
              setKey(prev => prev + 1);
              setState(data.state);
            }
          } else {
            setState(data.state);
          }
        })
        .catch(err => console.log(err));
    }, 1000);
    return () => clearInterval(interval);
  }, [state]);

  if (state === "male" || state === "female") {
    return <ResultView gender={state} keyVal={key} />;
  }

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