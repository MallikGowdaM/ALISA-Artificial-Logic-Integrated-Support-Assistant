import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import Login from "./Login.jsx";
import Signup from "./Signup.jsx";
import Dashboard from "./Dashboard.jsx";
import ArcReactor from "./ArcReactor";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/arc-reactor" element={<ArcReactor />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>

      {/* Toast notifications (dark theme) */}
      <ToastContainer
        position="top-right"
        autoClose={3000}
        theme="dark"
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </Router>
  );
}

export default App;
