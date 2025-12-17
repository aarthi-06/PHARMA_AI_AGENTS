import { useEffect, useRef, useState } from "react";

function ReportGenerator() {
  const [query, setQuery] = useState("");
  const [pdfUrl, setPdfUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [jobId, setJobId] = useState(null);
  const [statusText, setStatusText] = useState("");

  const pollRef = useRef(null);

  const clearPoll = () => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = null;
  };

  const cleanupPdf = () => {
    if (pdfUrl) URL.revokeObjectURL(pdfUrl);
    setPdfUrl(null);
  };

  useEffect(() => {
    return () => {
      clearPoll();
      cleanupPdf();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleGenerate = async () => {
    if (!query.trim()) return;

    setErr("");
    setLoading(true);
    setStatusText("Starting job...");
    setJobId(null);

    clearPoll();
    cleanupPdf();

    try {
      // 1) START
      const startRes = await fetch("/api/report/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_query: query }),
      });

      if (!startRes.ok) {
        const msg = await startRes.text();
        throw new Error(msg || "Failed to start report job");
      }

      const startJson = await startRes.json();
      const newJobId = startJson.jobId;
      if (!newJobId) throw new Error("No jobId returned from backend");

      setJobId(newJobId);
      setStatusText("Job started. Running CrewAI...");

      // 2) POLL STATUS every 2s
      pollRef.current = setInterval(async () => {
        try {
          const sRes = await fetch(`/api/report/status/${newJobId}`);
          if (!sRes.ok) {
            const msg = await sRes.text();
            throw new Error(msg || "Status check failed");
          }

          const sJson = await sRes.json();

          if (sJson.status === "running") {
            setStatusText("Generating report... (still running)");
            return;
          }

          if (sJson.status === "error") {
            clearPoll();
            setLoading(false);
            setErr(sJson.error || "Report generation failed");
            setStatusText("");
            return;
          }

          if (sJson.status === "done") {
            clearPoll();
            setStatusText("Downloading PDF...");

            // 3) DOWNLOAD PDF
            const dRes = await fetch(`/api/report/download/${newJobId}`);
            if (!dRes.ok) {
              const msg = await dRes.text();
              throw new Error(msg || "Download failed");
            }

            const blob = await dRes.blob();

            // filename from backend header (optional)
            const cd = dRes.headers.get("content-disposition") || "";
            const match = cd.match(/filename="(.+?)"/);
            const filename = match?.[1] || "report.pdf";
            console.log("PDF filename:", filename);

            const url = URL.createObjectURL(blob);
            setPdfUrl(url);

            setLoading(false);
            setStatusText("");
          }
        } catch (e) {
          // If polling fails (network/proxy), stop polling and show error
          clearPoll();
          setLoading(false);
          setErr(e.message || "Polling failed");
          setStatusText("");
        }
      }, 2000);
    } catch (e) {
      clearPoll();
      setLoading(false);
      setErr(e.message || "Failed to generate report");
      setStatusText("");
    }
  };

  return (
    <div className="report-container">
      <h1>AI Report Generator</h1>
      <p className="subtitle">
        Describe what you need and let AI create comprehensive reports instantly
      </p>

      <div className="query-box">
        <textarea
          placeholder="Evaluate repurposing potential of remdesivir for COVID-19 in India from 2019 to 2024"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          maxLength={500}
        />
        <div className="char-count">{query.length} characters</div>
      </div>

      <button className="generate-btn" onClick={handleGenerate} disabled={loading}>
        {loading ? "Generating..." : "✨ Generate Report"}
      </button>

      {/* status */}
      {loading && (
        <p style={{ marginTop: 10 }}>
          {statusText}
          {jobId ? (
            <span style={{ display: "block", fontSize: 12, opacity: 0.8 }}>
              Job ID: {jobId}
            </span>
          ) : null}
        </p>
      )}

      {/* error */}
      {err && <p style={{ marginTop: 10 }}>{err}</p>}

      {/* PDF preview */}
      {pdfUrl && (
        <div className="pdf-section">
          <h3>Generated Report</h3>
          <iframe src={pdfUrl} title="Generated PDF" width="100%" height="500px" />
        </div>
      )}
    </div>
  );
}

export default ReportGenerator;
