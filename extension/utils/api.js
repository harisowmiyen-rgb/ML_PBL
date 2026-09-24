const API_BASE_URL = "http://localhost:8000/api";

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.ok;
  } catch (err) {
    return false;
  }
}

export async function scanPage(payload) {
  try {
    const res = await fetch(`${API_BASE_URL}/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`Scan failed: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.error("[DPD API] Scan error:", err);
    throw err;
  }
}

export async function getReports() {
  try {
    const res = await fetch(`${API_BASE_URL}/reports`);
    if (!res.ok) throw new Error(`Fetch reports failed: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.error("[DPD API] Reports error:", err);
    return [];
  }
}

export async function sendFeedback(detectionId, feedback) {
  try {
    const res = await fetch(`${API_BASE_URL}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ detection_id: detectionId, user_feedback: feedback })
    });
    return res.ok;
  } catch (err) {
    console.error("[DPD API] Feedback error:", err);
    return false;
  }
}
