// src/controllers/report.controller.js

// const crewaiService = require("../services/crewai.service");
// const pdfService = require("../services/pdf.service");

// exports.generateReport = async (req, res) => {
//   try {
//     const { user_query } = req.body;

//     if (!user_query || typeof user_query !== "string") {
//       return res.status(400).json({ error: "user_query is required (string)." });
//     }

//     // 1) Call CrewAI service
//     const outputJson = await crewaiService.runCrewAI(user_query);

//     // 2) JSON -> PDF (buffer + filename)
//     const { buffer, fileName } = await pdfService.jsonToPdfBuffer(outputJson);

//     // 3) Send PDF to frontend
//     res.setHeader("Content-Type", "application/pdf");
//     res.setHeader("Content-Disposition", `attachment; filename="${fileName}"`);
    
//     return res.status(200).send(buffer);
    
//   } catch (err) {
//     console.error("generateReport error:", err?.message || err);
//     return res.status(500).json({ error: "Failed to generate report." });
//   }
// };



const crewaiService = require("../services/crewai.service");
const pdfService = require("../services/pdf.service");
const jobStore = require("../services/job.store");
const path = require("path");

exports.startReport = async (req, res) => {
  const { user_query } = req.body;

  if (!user_query || typeof user_query !== "string") {
    return res.status(400).json({ error: "user_query is required (string)." });
  }

  const jobId = jobStore.createJob();

  // ✅ respond immediately (no waiting, no timeout)
  res.status(202).json({ jobId });

  // ✅ background work
  (async () => {
    try {
      jobStore.setJob(jobId, { status: "running" });

      const outputJson = await crewaiService.runCrewAI(user_query);

      // save pdf + return path
      const { fileName, savedPath } = await pdfService.jsonToPdfBuffer(outputJson);

      jobStore.setJob(jobId, {
        status: "done",
        fileName,
        filePath: savedPath,
      });
    } catch (e) {
      jobStore.setJob(jobId, {
        status: "error",
        error: e?.message || String(e),
      });
    }
  })();
};

exports.getStatus = (req, res) => {
  const job = jobStore.getJob(req.params.jobId);
  if (!job) return res.status(404).json({ error: "Job not found" });

  // (optional) don’t expose full path to frontend
  const safe = {
    status: job.status,
    fileName: job.fileName,
    error: job.error,
  };

  return res.json(safe);
};

exports.download = (req, res) => {
  const job = jobStore.getJob(req.params.jobId);
  if (!job) return res.status(404).json({ error: "Job not found" });
  if (job.status !== "done") return res.status(409).json({ error: "Not ready" });

  res.setHeader("Content-Type", "application/pdf");
  res.setHeader("Content-Disposition", `attachment; filename="${job.fileName}"`);

  // ✅ sendFile needs absolute path
  return res.sendFile(path.resolve(job.filePath));
};


