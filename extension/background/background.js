// Background service worker for Dark Pattern Detector
chrome.runtime.onInstalled.addListener(() => {
  console.log("[DPD Background] Dark Pattern Detector extension installed.");
});

const tabScanResults = new Map();

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const tabId = sender.tab ? sender.tab.id : null;

  if (message.type === "SCAN_RESULTS_READY") {
    if (tabId) {
      tabScanResults.set(tabId, message.data);
      const count = message.data.total_patterns_detected || 0;
      
      if (count > 0) {
        chrome.action.setBadgeText({ tabId, text: String(count) });
        chrome.action.setBadgeBackgroundColor({
          tabId,
          color: message.data.risk_level === "High" ? "#e53e3e" : "#dd6b20"
        });
      } else {
        chrome.action.setBadgeText({ tabId, text: "OK" });
        chrome.action.setBadgeBackgroundColor({ tabId, color: "#38a169" });
      }
    }
    sendResponse({ status: "ACK" });
  }

  if (message.type === "GET_LATEST_SCAN") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs && tabs.length > 0) {
        const activeTabId = tabs[0].id;
        const result = tabScanResults.get(activeTabId) || null;
        sendResponse({ data: result });
      } else {
        sendResponse({ data: null });
      }
    });
    return true;
  }
});
