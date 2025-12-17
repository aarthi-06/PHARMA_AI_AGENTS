// src/services/crewai.service.js

const axios = require("axios");

exports.runCrewAI = async (user_query) => {
  const url = process.env.CREWAI_URL;
  if (!url) throw new Error("CREWAI_URL is missing in .env");

  const timeout = Number(process.env.CREWAI_TIMEOUT_MS || 60000);

  const resp = await axios.post(
    url,
    { user_query },
    {
      headers: { "Content-Type": "application/json" },
      timeout,
    }
  );

  // FastAPI usually returns JSON in resp.data
  return resp.data;
};
