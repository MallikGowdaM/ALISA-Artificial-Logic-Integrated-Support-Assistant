import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { toast } from "react-toastify";
import Lottie from "lottie-react";
import signupAnim from "./assets/signup.json";

export default function Signup() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPass] = useState("");
  const [confirmPassword, setConfirmPass] = useState("");
  const [message, setMsg] = useState("");
  const navigate = useNavigate();

  const handleSignup = async () => {
    if (!username || !email || !phone || !password || !confirmPassword) {
      toast.error("❌ All fields are required!");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("❌ Passwords do not match!");
      return;
    }

    const res = await fetch("http://localhost:4000/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, phone, password }),
    });
    const data = await res.json();

    if (data.success) {
      toast.success("🎉 Signup successful!");
      setMsg(data.message);
      setTimeout(() => navigate("/"), 1000);
    } else {
      toast.warning(`⚠️ ${data.message || "Account already exists"}`);
      setMsg(data.message);
    }
  };

  return (
    <div className="min-h-screen w-screen flex items-center justify-center bg-gradient-to-r from-pink-500 via-orange-400 to-yellow-400">
      <div className="bg-white/80 backdrop-blur-lg shadow-2xl rounded-2xl p-10 w-[400px] text-center">
        <Lottie animationData={signupAnim} loop style={{ height: 120 }} />
        <h2 className="text-3xl font-bold mb-6 text-pink-700">Create Account</h2>

       <form
  onSubmit={(e) => {
    e.preventDefault();
    handleSignup(); // ✅ Works on Enter key too
  }}
>
  <input
    className="border w-full p-3 mb-3 rounded focus:ring-2 focus:ring-pink-400"
    type="text"
    placeholder="Username"
    onChange={(e) => setUsername(e.target.value)}
  />

  <input
    className="border w-full p-3 mb-3 rounded focus:ring-2 focus:ring-pink-400"
    type="email"
    placeholder="Email"
    onChange={(e) => setEmail(e.target.value)}
  />

  <input
    className="border w-full p-3 mb-3 rounded focus:ring-2 focus:ring-pink-400"
    type="tel"
    placeholder="Phone Number"
    onChange={(e) => setPhone(e.target.value)}
  />

  <input
    className="border w-full p-3 mb-3 rounded focus:ring-2 focus:ring-pink-400"
    type="password"
    placeholder="Password"
    onChange={(e) => setPass(e.target.value)}
  />

  <input
    className="border w-full p-3 mb-3 rounded focus:ring-2 focus:ring-pink-400"
    type="password"
    placeholder="Confirm Password"
    onChange={(e) => setConfirmPass(e.target.value)}
  />

  <button
    type="submit" // ✅ Important: allows Enter key to work
    className="bg-pink-600 hover:bg-pink-700 text-white w-full py-3 rounded-xl font-semibold transition"
  >
    Signup
  </button>
</form>


        {message && <p className="text-green-600 mt-3">{message}</p>}

        <p className="mt-6 text-gray-700">
          Already registered?{" "}
          <Link to="/" className="text-pink-700 hover:underline">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
