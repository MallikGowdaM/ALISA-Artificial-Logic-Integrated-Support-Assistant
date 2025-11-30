import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { toast } from "react-toastify";
import Lottie from "lottie-react";
import loginAnim from "./assets/login.json";
import { Eye, EyeOff } from "lucide-react"; // 👁️ eye icons

export default function Login() {
  const [identifier, setIdentifier] = useState(""); // username or email
  const [password, setPass] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    if (!identifier || !password) {
      toast.error("❌ All fields are required!");
      return;
    }

    const res = await fetch("http://localhost:4000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier, password }),
    });
    const data = await res.json();

    if (data.success) {
      toast.success("✅ Login successful!");
      navigate("/arc-reactor");
    } else {
      toast.error(`❌ Login failed: ${data.message}`);
      setError(data.message);
    }
  };

  return (
    <div className="min-h-screen w-screen flex items-center justify-center bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
      <div className="bg-white/80 backdrop-blur-lg shadow-2xl rounded-2xl p-10 w-[400px] text-center">
        <Lottie animationData={loginAnim} loop style={{ height: 120 }} />
        <h2 className="text-3xl font-bold mb-6 text-indigo-700">Welcome Back!</h2>

    <form
  onSubmit={(e) => {
    e.preventDefault();
    handleLogin(); // form submission + Enter key
  }}
>
  {/* Username / Email */}
  <input
    className="border w-full p-3 mb-3 rounded focus:ring-2 focus:ring-indigo-400"
    type="text"
    placeholder="Username or Email"
    onChange={(e) => setIdentifier(e.target.value)}
  />

  {/* Password with Eye Button */}
  <div className="relative w-full mb-3">
    <input
      className="border w-full p-3 rounded focus:ring-2 focus:ring-indigo-400 pr-12"
      type={showPassword ? "text" : "password"}
      placeholder="Password"
      onChange={(e) => setPass(e.target.value)}
    />
    <button
      type="button" // ✅ prevents Enter from triggering this
      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-indigo-600"
      onMouseDown={() => setShowPassword(true)}
      onMouseUp={() => setShowPassword(false)}
      onMouseLeave={() => setShowPassword(false)}
      onTouchStart={() => setShowPassword(true)}
      onTouchEnd={() => setShowPassword(false)}
    >
      {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
    </button>
  </div>

  {/* ✅ Submit button — Enter key now works */}
  <button
    type="submit"
    className="bg-indigo-600 hover:bg-indigo-700 text-white w-full py-3 rounded-xl font-semibold transition"
  >
    Login
  </button>
</form>


        {error && <p className="text-red-600 mt-3">{error}</p>}

        <p className="mt-6 text-gray-700">
          New here?{" "}
          <Link to="/signup" className="text-indigo-700 hover:underline">
            Create an Account
          </Link>
        </p>
      </div>
    </div>
  );
}
