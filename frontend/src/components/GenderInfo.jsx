'use client';
import { motion } from 'framer-motion';
import * as React from 'react';
import {
  Venus,
  Mars,
  Sparkles,
  ShieldCheck,
  ScanFace,
  Brain,
  HeartHandshake,
} from 'lucide-react';
import "./GenderInfo.css";

const MALE_POINTS = [
  { icon: <ShieldCheck />, text: "Confident posture and steady presence" },
  { icon: <ScanFace />, text: "Clear facial features with calm expression" },
  { icon: <Brain />, text: "Reflects strength and determination" },
  { icon: <Sparkles />, text: "Suitable for leadership and responsibility" },
];

const FEMALE_POINTS = [
  { icon: <Sparkles />, text: "Graceful posture with confident appearance" },
  { icon: <ScanFace />, text: "Calm and expressive facial features" },
  { icon: <HeartHandshake />, text: "Reflects warmth and resilience" },
  { icon: <Brain />, text: "Shows creativity and leadership qualities" },
];

function GenderInfo({ gender, keyVal }) {
  const isMale = gender === "male";
  const points = isMale ? MALE_POINTS : FEMALE_POINTS;
  const title = isMale ? "MALE" : "FEMALE";
  const desc = isMale
    ? "A man appears confident and composed, standing calmly before the camera. His facial features are clear, and his presence reflects strength, determination, and a steady personality suitable for leadership and responsibility. His posture suggests discipline and focus, while his expression conveys confidence and clarity of thought. Overall, he presents an image of reliability, resilience, and a strong sense of purpose."
    : "A woman appears confident and graceful, standing naturally before the camera. Her facial expression reflects calmness and intelligence, conveying warmth, resilience, and a strong personality suited for creativity and leadership. Her composed posture highlights confidence and poise, while her gentle expression suggests empathy and determination. Overall, she represents balance, strength, and a thoughtful presence that inspires trust and positivity.";

  return (
    <div className={`gender-info-page ${isMale ? "male-theme" : "female-theme"}`} key={keyVal}>
      <motion.section
        className="gender-info-shell"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
      >
        <header className="gender-header">
          <h1 className="gender-main-title">{title}</h1>
          <p className="gender-description">{desc}</p>
        </header>

        <div className="traits-grid">
          {points.map((pt, i) => (
            <motion.div
              key={i}
              className="trait-item"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.18 + (i * 0.08), duration: 0.32 }}
            >
              {/* <div className="trait-icon">
                {React.cloneElement(pt.icon, { strokeWidth: 2, size: 20 })}
              </div> */}
              <span className="trait-text">{pt.text}</span>
            </motion.div>
          ))}
        </div>
      </motion.section>
    </div>
  );
}

export default GenderInfo;
