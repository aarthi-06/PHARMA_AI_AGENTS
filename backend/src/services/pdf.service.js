// // src/services/pdf.service.js
// const fs = require("fs");
// const path = require("path");
// const React = require("react");
// const ReactPDF = require("@react-pdf/renderer"); // 👈 import whole module

// const ReportPdf = require("../../templates/ReportPdf");

// function safeFileName(name) {
//   return String(name || "report")
//     .normalize("NFKD")                 // split accented/unicode chars
//     .replace(/[^\x00-\x7F]/g, "-")     // remove non-ASCII (– etc)
//     .replace(/[<>:"/\\|?*\x00-\x1F]/g, "")
//     .replace(/\s+/g, " ")
//     .trim()
//     .replace(/ +/g, "_")               // spaces -> _
//     .slice(0, 120) || "report";
// }


// exports.jsonToPdfBuffer = async (outputJson) => {
//   console.log("✅ Using React-PDF service:", __filename);

//   const report =
//   outputJson?.report?.report ||  // ✅ your current API wrapper
//   outputJson?.report ||          // fallback if API returns only {report:{...}}
//   outputJson;                    // fallback if API returns the report directly

//   const title = report.title || report.report_id || "CrewAI Report";

//   const element = React.createElement(ReportPdf, { report });

//   // ✅ This returns a real Node Buffer
//   const buffer = await ReactPDF.renderToBuffer(element);

//   console.log("✅ React-PDF buffer?", Buffer.isBuffer(buffer), buffer?.constructor?.name);

//  const fileName = `${safeFileName(title)}.pdf`;


//   // optional save
//   const dir = path.join(__dirname, "../../storage/reports");
//   fs.mkdirSync(dir, { recursive: true });
//   fs.writeFileSync(path.join(dir, fileName), buffer);

//   return { buffer, fileName };
// };











const fs = require("fs");
const path = require("path");
const React = require("react");
const ReactPDF = require("@react-pdf/renderer");

const ReportPdf = require("../../templates/ReportPdf");

/**
 * Make filename safe for HTTP headers + filesystem
 */
function safeFileName(name) {
  return String(name || "report")
    .normalize("NFKD")
    .replace(/[^\x00-\x7F]/g, "-")
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/ +/g, "_")
    .slice(0, 120) || "report";
}

exports.jsonToPdfBuffer = async (outputJson) => {
  console.log("✅ Using React-PDF service:", __filename);

  // 🔑 normalize CrewAI response shape
  const report =
    outputJson?.report?.report ||
    outputJson?.report ||
    outputJson;

  if (!report || typeof report !== "object") {
    throw new Error("Invalid report data received from CrewAI");
  }

  const title = report.title || report.report_id || "CrewAI_Report";

  // 🔹 Create React-PDF element
  const element = React.createElement(ReportPdf, { report });

  // 🔹 Render PDF -> Node Buffer
  const buffer = await ReactPDF.renderToBuffer(element);

  console.log(
    "✅ React-PDF buffer created:",
    Buffer.isBuffer(buffer),
    buffer?.constructor?.name
  );

  // 🔹 File handling
  const fileName = `${safeFileName(title)}.pdf`;
  const dir = path.join(__dirname, "../../storage/reports");

  fs.mkdirSync(dir, { recursive: true });

  const savedPath = path.join(dir, fileName);
  fs.writeFileSync(savedPath, buffer);

  console.log("📄 PDF saved at:", savedPath);

  // 🔹 return everything controller needs
  return {
    buffer,
    fileName,
    savedPath, // ✅ required for /download/:jobId
  };
};
