import express from "express";
import sqlite3 from "sqlite3";
import { open } from "sqlite";
import cors from "cors";
import bodyParser from "body-parser";
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";
import { Server } from "socket.io";
import { createServer } from "http";

let assistantProcess = null;

const app = express();
app.use(cors());
app.use(bodyParser.json());

// ----------------------
// Database setup
// ----------------------
const db = await open({
  filename: "./database.db",
  driver: sqlite3.Database,
});

await db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    phone TEXT UNIQUE,
    password TEXT
  )
`);

// ----------------------
// HTTP + WebSocket server
// ----------------------
const httpServer = createServer(app);
const io = new Server(httpServer, { cors: { origin: "*" } });

// ----------------------
// Socket.IO bridge
// ----------------------
io.on("connection", (socket) => {
  console.log("✅ Frontend connected");

  // Forward assistant status from Python → all clients
   socket.on("assistant_status", (data) => {
    console.log("Assistant status:", data); // debug log
    io.emit("assistant_status", data);
  });
  // ✅ NEW: Handle typed commands from frontend
  socket.on("typed_command", (command) => {
    console.log("📥 Typed command from frontend:", command);

    // Forward typed command to Python
    io.emit("typed_command", command);

    // Also display it in UI as user_command
    io.emit("assistant_status", {
      status: "user_command",
      command_text: command,
    });
  });
});

// ----------------------
// Auth routes
// ----------------------
app.post("/signup", async (req, res) => {
  const { username, email, phone, password } = req.body;
  try {
    await db.run(
      "INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)",
      [username, email, phone, password]
    );
    res.json({ success: true, message: "Signup successful" });
  } catch (err) {
    res.json({ success: false, message: "Account already exists" });
  }
});

app.post("/login", async (req, res) => {
  const { identifier, password } = req.body;
  const user = await db.get(
    "SELECT * FROM users WHERE (email = ? OR username = ?) AND password = ?",
    [identifier, identifier, password]
  );
  if (user) res.json({ success: true });
  else res.json({ success: false, message: "Invalid credentials" });
});

// ----------------------
// Assistant route
// ----------------------
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.post("/start-assistant", (req, res) => {
  if (assistantProcess) {
    return res.json({ success: false, message: "Assistant already running" });
  }

  const pythonPath = path.join(__dirname, "../assistant/main.py");
  assistantProcess = spawn("python", [pythonPath]); // ✅ store globally

  assistantProcess.stdout.on("data", (data) => {
    const msg = data.toString().trim();
    console.log(`Assistant: ${msg}`);

    if (msg.includes("WAKEWORD_DETECTED")) {
      io.emit("wakeword", { success: true });
    }
  });

  assistantProcess.stderr.on("data", (data) => {
    console.error(`Assistant Error: ${data}`);
  });

  assistantProcess.on("close", (code) => {
    console.log(`Assistant stopped with code ${code}`);
    assistantProcess = null; // ✅ reset when stopped
  });

  res.json({ success: true, message: "Assistant started, waiting for wake word..." });
});

app.post("/stop-assistant", (req, res) => {
  if (assistantProcess) {
    assistantProcess.kill("SIGTERM");
    assistantProcess = null;
    console.log("🛑 Assistant stopped manually");
    return res.json({ success: true, message: "Assistant stopped" });
  } else {
    return res.json({ success: false, message: "No assistant running" });
  }
});

// ----------------------
// Start server
// ----------------------
const PORT = 4000;
httpServer.listen(PORT, () =>
  console.log(`✅ Backend running on http://localhost:${PORT}`)
);
