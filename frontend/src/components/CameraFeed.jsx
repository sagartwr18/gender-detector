'use client';
import { useEffect, useState, useRef } from "react";
import { motion, useInView } from 'framer-motion';
import * as React from 'react';
import "./CameraFeed.css";

function TextFade({
  direction,
  children,
  className = '',
  staggerChildren = 0.1,
}) {
  const FADE_DOWN = {
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 100, damping: 20 } },
    hidden: { opacity: 0, y: direction === 'down' ? -18 : 18 },
  };
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });
  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={isInView ? 'show' : ''}
      variants={{
        hidden: {},
        show: {
          transition: {
            staggerChildren: staggerChildren,
          },
        },
      }}
      className={className}
    >
      {React.Children.map(children, (child) =>
        React.isValidElement(child) ? (
          <motion.div variants={FADE_DOWN}>{child}</motion.div>
        ) : (
          child
        )
      )}
    </motion.div>
  );
}

function CameraFeed(){

  const [state,setState] = useState("camera");
  const [key, setKey] = useState(0);

  useEffect(()=>{

    const interval = setInterval(()=>{

        fetch("http://127.0.0.1:8000/state")
        .then(res=>res.json())
        .then(data=>{
          console.log("API STATE:", data.state)
          if(data.state === "male" || data.state === "female"){
            if(state !== data.state){
              setKey(prev => prev + 1);
              setState(data.state);
            }
          } else {
            setState(data.state);
          }
        })
        .catch(err=>console.log(err))

    },1000)

    return ()=>clearInterval(interval)

  },[state])

  if(state === "male"){
    return(
      <div className="camera-page">
        <div className={`fullscreen-content male-content`} key={key}>
          <TextFade direction="up" staggerChildren={0.15} className="fade-content">
            <h2 className="result-title">Male</h2>
            <p className="result-paragraph">
              A man appears confident and composed, standing calmly before the camera. His facial features are clear, and his presence reflects strength, determination, and a steady personality suitable for leadership and responsibility.
            </p>
            <ul className="result-points">
              <li>Confident posture and steady presence</li>
              <li>Clear facial features with calm expression</li>
              <li>Reflects strength, determination, and focus</li>
              <li>Suitable for leadership and responsibility</li>
            </ul>
          </TextFade>
        </div>
      </div>
    )
  }

  if(state === "female"){
    return(
      <div className="camera-page">
        <div className={`fullscreen-content female-content`} key={key}>
          <TextFade direction="up" staggerChildren={0.15} className="fade-content">
            <h2 className="result-title">Female</h2>
            <p className="result-paragraph">
              A woman appears confident and graceful, standing naturally before the camera. Her facial expression reflects calmness and intelligence, conveying warmth, resilience, and a strong personality suited for creativity and leadership.
            </p>
            <ul className="result-points">
              <li>Graceful posture with confident appearance</li>
              <li>Calm and expressive facial features</li>
              <li>Reflects warmth, intelligence, and resilience</li>
              <li>Shows creativity and strong leadership qualities</li>
            </ul>
          </TextFade>
        </div>
      </div>
    )
  }

  return(
    <div className="camera-page">
      <div className="camera-card">
        <div className="video-section">
          <img src="http://127.0.0.1:8000/video" alt="Camera" className="frame-image"/>
        </div>
        <div className="info-section">
          <h3 className="info-title">Instructions</h3>
          <ul className="instructions-list">
            <li>Position your face in the center of the frame</li>
            <li>Ensure good lighting on your face</li>
            <li>Remove glasses or hats for better accuracy</li>
            <li>Look directly at the camera</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default CameraFeed
