import { checkHealth, getReports } from "../utils/api.js";

document.addEventListener("DOMContentLoaded", async () => {
  const backendStatusEl = document.getElementById("backend-status");
  const siteHostnameEl = document.getElementById("site-hostname");
  const riskBadgeEl = document.getElementById("risk-badge");
  const riskScoreEl = document.getElementById("risk-score");
  const patternCountEl = document.getElementById("pattern-count");
  const detectionsListEl = document.getElementById("detections-list");
  const historyListEl = document.getElementById("history-list");
  const btnScan = document.getElementById("btn-scan");
  const btnClear = document.getElementById("btn-clear");
  const tabScan = document.getElementById("tab-scan");
  const tabHistory = document.getElementById("tab-history");
  const scanView = document.getElementById("scan-view");
  const historyView = document.getElementById("history-view");
  const docsLink = document.getElementById("docs-link");

  if (docsLink) {
    docsLink.onclick = () => chrome.tabs.create({ url: "http://localhost:8000/docs" });
  }

  try {
    const isHealthy = await checkHealth();
    if (isHealthy) {
      backendStatusEl.innerText = "API Online";
      backendStatusEl.className = "status-pill online";
    } else {
      backendStatusEl.innerText = "API Offline";
      backendStatusEl.className = "status-pill offline";
    }
  } catch (e) {
    backendStatusEl.innerText = "API Offline";
    backendStatusEl.className = "status-pill offline";
  }

  const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (activeTab && activeTab.url) {
    try {
      const urlObj = new URL(activeTab.url);
      siteHostnameEl.innerText = urlObj.hostname;
    } catch (e) {
      siteHostnameEl.innerText = "Webpage";
    }
  }

  function renderScanData(data) {
    if (!data) return;
    riskScoreEl.innerText = Math.round(data.overall_risk_score || 0);
    const count = data.total_patterns_detected || 0;
    patternCountEl.innerText = count;

    const level = (data.risk_level || "LOW").toUpperCase();
    riskBadgeEl.innerText = level;
    riskBadgeEl.className = `risk-badge ${level.toLowerCase()}`;

    if (!data.detections || data.detections.length === 0) {
      detectionsListEl.innerHTML = `<div class="empty-state">✓ No manipulative dark patterns identified on this page.</div>`;
      return;
    }

    detectionsListEl.innerHTML = data.detections.map(d => `
      <div class="detection-item">
        <div class="detection-header">
          <span class="detection-type ${(d.severity || "medium").toLowerCase()}">
            🔴 ${d.type}
          </span>
          <span class="confidence-tag">${Math.round(d.confidence * 100)}%</span>
        </div>
        <div class="detection-snippet">"${d.text}"</div>
        <div class="detection-reason">${d.explanation}</div>
      </div>
    `).join("");
  }

  chrome.runtime.sendMessage({ type: "GET_LATEST_SCAN" }, (res) => {
    if (res && res.data) {
      renderScanData(res.data);
    }
  });

  btnScan.onclick = () => {
    btnScan.innerText = "Scanning...";
    btnScan.disabled = true;

    chrome.tabs.sendMessage(activeTab.id, { type: "TRIGGER_SCAN" }, (res) => {
      btnScan.innerText = "🔍 Scan Page";
      btnScan.disabled = false;
      if (res && res.data) {
        renderScanData(res.data);
      }
    });
  };

  btnClear.onclick = () => {
    chrome.tabs.sendMessage(activeTab.id, { type: "CLEAR_HIGHLIGHTS" }, () => {
      riskScoreEl.innerText = "0";
      patternCountEl.innerText = "0";
      riskBadgeEl.innerText = "CLEARED";
      riskBadgeEl.className = "risk-badge";
      detectionsListEl.innerHTML = `<div class="empty-state">Highlights cleared from page.</div>`;
    });
  };

  tabScan.onclick = () => {
    tabScan.classList.add("active");
    tabHistory.classList.remove("active");
    scanView.style.display = "block";
    historyView.style.display = "none";
  };

  tabHistory.onclick = async () => {
    tabHistory.classList.add("active");
    tabScan.classList.remove("active");
    scanView.style.display = "none";
    historyView.style.display = "block";

    historyListEl.innerHTML = `<div class="empty-state">Fetching scan history...</div>`;
    const reports = await getReports();
    if (!reports || reports.length === 0) {
      historyListEl.innerHTML = `<div class="empty-state">No historical scans recorded.</div>`;
      return;
    }

    historyListEl.innerHTML = reports.map(r => `
      <div class="history-item">
        <div>
          <div class="history-url">${r.url}</div>
          <div class="history-meta">${new Date(r.scan_time).toLocaleDateString()} · ${r.total_patterns_detected} patterns</div>
        </div>
        <span class="risk-badge ${(r.risk_level || "low").toLowerCase()}">${r.risk_level} (${Math.round(r.overall_risk_score)})</span>
      </div>
    `).join("");
  };
});
