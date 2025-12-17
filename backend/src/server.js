// src/server.js

const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");

dotenv.config();

const app = express();

// ====== MIDDLEWARES ======

app.use(
  cors({
    origin: "http://localhost:5173", // Vite frontend
    methods: ["GET", "POST"],
    allowedHeaders: ["Content-Type"],
    exposedHeaders: ["Content-Disposition"], // 👈 REQUIRED for PDF filename
  })
);





app.use(express.json());

// ====== ROUTES ======
const reportRoutes = require("./routes/report.routes");
app.use("/api/report", reportRoutes);

// ====== HEALTH CHECK ======
app.get("/", (req, res) => {
  res.json({ status: "Backend running 🚀" });
});

// ====== SERVER START ======
const PORT = process.env.PORT || 5001;

const server= app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

server.requestTimeout = 7 * 60 * 1000;
server.setTimeout(7 * 60 * 1000);