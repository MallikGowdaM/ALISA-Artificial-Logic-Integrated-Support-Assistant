import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Lottie from "lottie-react";
import arcAnim from "./assets/arc.json";
import arcSound from "./assets/arc-sound.mp3"; // ✅ add sound file
import { io } from "socket.io-client";

const socket = io("http://localhost:4000");

export default function ArcReactor() {
  const [status, setStatus] = useState("");
  const [activeSpeaker, setActiveSpeaker] = useState(null);
  const [activeText, setActiveText] = useState("");
  const [animationClass, setAnimationClass] = useState("fade-in");

  const navigate = useNavigate();
  const audioRef = useRef(null);

  useEffect(() => {
    socket.on("wakeword", (data) => {
      if (data.success) {
        navigate("/dashboard");
      }
    });

    socket.on("assistant_status", (data) => {
      console.log("ArcReactor received:", data);

      if (data.status === "user_command" && data.command_text) {
        setActiveSpeaker("user");
        setActiveText(data.command_text);
        setAnimationClass("fade-in");
        if (data.command_text.toLowerCase() === "exit") {
          setActiveText("");
          setActiveSpeaker(null);
        }
      }

      if (data.status === "assistant_command" && data.command_text) {
        setActiveSpeaker("assistant");
        setActiveText(data.command_text);
        setAnimationClass("fade-in");
      }

      if (data.status === "reset") {
        setActiveText("");
        setActiveSpeaker(null);
      }
    });

    return () => {
      socket.off("wakeword");
      socket.off("assistant_status");
    };
  }, [navigate]);

  useEffect(() => {
    if (activeText) {
      const timer = setTimeout(() => {
        setAnimationClass("fade-out");
        setTimeout(() => {
          setActiveText("");
          setActiveSpeaker(null);
        }, 800);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [activeText]);

  const startAssistant = async () => {
    try {
      // ✅ Play sound on click
      if (audioRef.current) {
        audioRef.current.currentTime = 0;
        audioRef.current.play();
      }

      const res = await fetch("http://localhost:4000/start-assistant", {
        method: "POST",
      });
      const data = await res.json();
      setStatus(data.message);
    } catch (err) {
      setStatus("❌ Could not start assistant");
    }
  };

  return (
    <div className="w-screen h-screen flex flex-col items-center justify-center bg-black relative">
      {/* Hidden audio element */}
      <audio ref={audioRef} src={arcSound} preload="auto" />

      {/* Arc animation */}
      <div className="cursor-pointer" onClick={startAssistant}>
        <Lottie
          animationData={arcAnim}
          loop
          style={{ width: "600px", height: "auto" }}
        />
      </div>

      {/* Real-time text */}
      {activeText && (
        <div
          className={`absolute bottom-10 mx-auto left-0 right-0
                      text-center text-2xl font-semibold italic ${animationClass}`}
          style={{
            fontFamily: "Poppins, sans-serif",
            letterSpacing: "0.5px",
            color: activeSpeaker === "user" ? "#60a5fa" : "#c084fc",
          }}
        >
          {activeSpeaker === "user" ? "🧑 " : "⚡ "} {activeText}
        </div>
      )}

      {/* Status */}
      {status && <p className="text-cyan-400 mt-6 text-lg">{status}</p>}
    </div>
  );
}
