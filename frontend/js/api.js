/**
 * Backend API client — all ML work happens on the server.
 */
const API_BASE = window.API_BASE || "http://127.0.0.1:8000";

export async function analyzeSample(params) {
  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE}/api/sample/analyze?${qs}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function analyzeUpload(file, params) {
  const form = new FormData();
  form.append("file", file);
  form.append("min_support", params.min_support);
  form.append("min_confidence", params.min_confidence);
  form.append("min_lift", params.min_lift);
  const res = await fetch(`${API_BASE}/api/analyze`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  return res.json();
}
