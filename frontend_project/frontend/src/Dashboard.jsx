import React, { useEffect, useState } from "react";
import Lottie from "lottie-react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { io } from "socket.io-client";
import siriWaves from "./assets/siri.json";

const socket = io("http://localhost:4000");

export default function Dashboard() {
  const [robotAnim, setRobotAnim] = useState(null);
  const [showWelcome, setShowWelcome] = useState(true);
  const [assistantStatus, setAssistantStatus] = useState("idle");
  const [activeSpeaker, setActiveSpeaker] = useState(null);
  const [activeText, setActiveText] = useState("");
  const [animationClass, setAnimationClass] = useState("fade-in");
  const [exitTriggered, setExitTriggered] = useState(false); // ✅ new flag

  const navigate = useNavigate();

  // Load robot + welcome
  useEffect(() => {
    fetch("/robot.json")
      .then((res) => res.json())
      .then((data) => setRobotAnim(data));

    const timer = setTimeout(() => setShowWelcome(false), 3000);
    return () => clearTimeout(timer);
  }, []);

  // Handle assistant events
 useEffect(() => {
  socket.on("assistant_status", (data) => {
    console.log("Frontend received status:", data);

    if (data.status) setAssistantStatus(data.status);

    if (data.status === "reset") {
      setActiveText("");
      setActiveSpeaker(null);
    }

    if (data.status === "user_command" && data.command_text) {
      setActiveSpeaker("user");
      setActiveText(data.command_text);
      setAnimationClass("fade-in");

      // ✅ Immediately navigate if user said "exit"
      if (data.command_text.toLowerCase() === "exit") {
        setActiveText("");
        setActiveSpeaker(null);
        setAssistantStatus("idle");
        navigate("/arc-reactor");
        return; // stop further handling
      }
    }

    if (data.status === "assistant_command" && data.command_text) {
      const delay =
        activeSpeaker === "user" && activeText
          ? Math.min(Math.max(activeText.length * 50, 1000), 4000)
          : 1000;

      setTimeout(() => {
        setActiveSpeaker("assistant");
        setActiveText(data.command_text);
        setAnimationClass("fade-in");
      }, delay);
    }
  });

  return () => socket.off("assistant_status");
}, [activeText, activeSpeaker, navigate]);

    // ✅ Handle navigation in separate effect
   useEffect(() => {
      if (exitTriggered) {
        setActiveText("");
        setActiveSpeaker(null);
        setAssistantStatus("idle");
        setExitTriggered(false);
        navigate("/arc-reactor"); // go to Arc Reactor wake-word page
      }
    }, [exitTriggered, navigate]);

  // Auto fade-out after 5s
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

  const logout = async () => {
  toast.info("🚪 Logged out successfully!");

  try {
    await fetch("http://localhost:4000/stop-assistant", { method: "POST" });
  } catch (err) {
    console.error("Failed to stop assistant:", err);
  }

  setActiveText("");
  setActiveSpeaker(null);
  setAssistantStatus("idle");
    navigate("/");
  };

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-black">
      {robotAnim && (
        <Lottie
          animationData={robotAnim}
          loop
          className="absolute inset-0 w-full h-full object-cover"
        />
      )}

      <div className="absolute inset-0 bg-black/40"></div>

      {/* Siri waves */}
      {(assistantStatus === "listening" || assistantStatus === "speaking") && (
        <div className="absolute bottom-7 w-full flex justify-center">
          <Lottie animationData={siriWaves} loop className="w-[500px] h-[100px]" />
        </div>
      )}

      {/* Real-time conversation text */}
      {activeText && (
        <div
          className={`absolute bottom-2 mx-auto left-0 right-0
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

      {/* Welcome popup */}
      {showWelcome && (
        <div className="absolute inset-0 flex items-center justify-center">
          <h2 className="text-4xl font-bold text-white drop-shadow-lg animate-fadeInOut">
            Welcome to Dashboard 🎉
          </h2>
        </div>
      )}

      {/* Logout button */}
      <button
        className="absolute bottom-6 right-6 bg-red-500 hover:bg-red-600 text-white
                   px-6 py-3 rounded-xl text-lg transition"
        onClick={logout}
      >
        Logout
      </button>
    </div>
  );
}
