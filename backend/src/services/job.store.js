const jobs = new Map();
// job = { status: "queued"|"running"|"done"|"error", filePath, fileName, error }

exports.createJob = () => {
  const id = `JOB-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  jobs.set(id, { status: "queued" });
  return id;
};

exports.setJob = (id, patch) => {
  const prev = jobs.get(id) || {};
  jobs.set(id, { ...prev, ...patch });
};

exports.getJob = (id) => jobs.get(id);
