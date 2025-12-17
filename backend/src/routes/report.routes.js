// src/routes/report.routes.js

// const express = require("express");
// const router = express.Router();

// const reportController = require("../controllers/report.controller");

// // POST /api/report/generate
// router.post("/generate", reportController.generateReport);

// module.exports = router;


const router = require("express").Router();
const report = require("../controllers/report.controller");

router.post("/start", report.startReport);
router.get("/status/:jobId", report.getStatus);
router.get("/download/:jobId", report.download);

module.exports = router;
