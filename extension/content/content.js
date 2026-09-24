// Real-time DOM inspection and Dark Pattern Highlight Script
(function () {
  const API_ENDPOINT = "http://localhost:8000/api/scan";
  let activeTooltip = null;

  function getCssSelector(el) {
    if (el.id) return '#' + el.id;
    if (el.tagName.toLowerCase() === "body") return "body";
    let path = el.tagName.toLowerCase();
    if (el.className && typeof el.className === "string") {
      const classes = el.className.trim().split(/\s+/).filter(c => !c.startsWith("dpd-"));
      if (classes.length > 0) path += "." + classes.slice(0, 2).join(".");
    }
    return path;
  }

  function detectDynamicTimers() {
    const timerNodes = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
    let node;
    const timePattern = /\b(?:\d{1,2}:\d{2}(?::\d{2})?)\b/;

    while ((node = walker.nextNode())) {
      if (["SCRIPT", "STYLE", "NOSCRIPT"].includes(node.tagName)) continue;
      const text = node.innerText || "";
      if (text.length < 50 && timePattern.test(text)) {
        if (node.children.length === 0 || Array.from(node.children).every(c => !timePattern.test(c.innerText))) {
          timerNodes.push({ element: node, text: text.trim(), selector: getCssSelector(node), isTimer: true });
        }
      }
    }
    return timerNodes;
  }

  function extractTargetDOMElements() {
    const elements = [];
    const seen = new Set();
    const timers = detectDynamicTimers();
    timers.forEach(t => {
      elements.push({ text: t.text, tag: t.element.tagName.toLowerCase(), selector: t.selector, attributes: { has_timer: true } });
      seen.add(t.element);
    });

    const query = "button, a, input[type='checkbox'], .banner, .alert, .deal, .stock, .countdown, .urgency, p, span, h2, h3, h4";
    const candidates = document.querySelectorAll(query);
    candidates.forEach(el => {
      if (seen.has(el) || el.closest(".dpd-tooltip-modal") || el.classList.contains("dpd-badge")) return;
      const text = (el.innerText || el.value || "").trim();
      if (text.length >= 6 && text.length <= 250) {
        const lower = text.toLowerCase();
        const isSuspicious = 
          lower.includes("only") || lower.includes("left") || lower.includes("hurry") ||
          lower.includes("expire") || lower.includes("ends in") || lower.includes("fee") ||
          lower.includes("charge") || lower.includes("no thanks") || lower.includes("uncheck") ||
          lower.includes("auto-renew") || lower.includes("protection") || lower.includes("viewing") ||
          lower.includes("exclusive") || lower.includes("sold out") || lower.includes("surcharge");

        if (isSuspicious) {
          elements.push({
            text: text,
            tag: el.tagName.toLowerCase(),
            selector: getCssSelector(el),
            attributes: { checked: el.type === "checkbox" ? el.checked : false }
          });
          seen.add(el);
        }
      }
    });
    return elements.slice(0, 50);
  }

  function applyVisualHighlights(detections) {
    removeVisualHighlights();
    detections.forEach(det => {
      let targetEl = null;
      if (det.html_selector) {
        try { targetEl = document.querySelector(det.html_selector); } catch (e) {}
      }
      if (!targetEl && det.text) {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
        let node;
        while ((node = walker.nextNode())) {
          if (node.innerText && node.innerText.trim().includes(det.text.trim())) {
            targetEl = node;
            break;
          }
        }
      }
      if (targetEl) {
        const severity = (det.severity || "medium").toLowerCase();
        targetEl.classList.add("dpd-highlight-" + severity);
        const badge = document.createElement("div");
        badge.className = "dpd-badge dpd-badge-" + severity;
        badge.innerHTML = "⚠️ " + det.type + " (" + Math.round(det.confidence * 100) + "%)";
        badge.onclick = (e) => {
          e.stopPropagation();
          showTooltipModal(det, targetEl, badge);
        };
        const compStyle = window.getComputedStyle(targetEl);
        if (compStyle.position === "static") targetEl.style.position = "relative";
        targetEl.appendChild(badge);
      }
    });
  }

  function showTooltipModal(detection, anchorEl, badgeEl) {
    if (activeTooltip) { activeTooltip.remove(); activeTooltip = null; }
    const modal = document.createElement("div");
    modal.className = "dpd-tooltip-modal";
    const severity = (detection.severity || "medium").toLowerCase();
    modal.innerHTML = `
      <div class="dpd-tooltip-header">
        <div class="dpd-tooltip-title ${severity}"><span>⚠️</span><span>${detection.type}</span></div>
        <button class="dpd-tooltip-close">&times;</button>
      </div>
      <div class="dpd-tooltip-body">
        <div style="margin-bottom:6px;">
          <span class="dpd-tooltip-confidence">Confidence: ${Math.round(detection.confidence * 100)}%</span>
          <span class="dpd-tooltip-confidence" style="margin-left:4px;">Severity: ${detection.severity}</span>
        </div>
        <p style="margin:6px 0 0 0;"><strong>Why:</strong> ${detection.explanation}</p>
        <p style="margin:4px 0 0 0;font-size:11px;color:#718096;"><em>"${detection.text}"</em></p>
      </div>
      <div class="dpd-tooltip-footer">
        <span>Accurate detection?</span>
        <div>
          <button class="dpd-feedback-btn" data-vote="Correct">✓ Yes</button>
          <button class="dpd-feedback-btn" data-vote="Incorrect">✗ False Alarm</button>
        </div>
      </div>
    `;

    modal.querySelector(".dpd-tooltip-close").onclick = () => modal.remove();
    modal.querySelectorAll(".dpd-feedback-btn").forEach(btn => {
      btn.onclick = async () => {
        const vote = btn.getAttribute("data-vote");
        btn.innerText = "Submitted!";
        btn.disabled = true;
        if (detection.id) {
          try {
            await fetch("http://localhost:8000/api/feedback", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ detection_id: detection.id, user_feedback: vote })
            });
          } catch (err) {}
        }
        setTimeout(() => modal.remove(), 1200);
      };
    });
    document.body.appendChild(modal);
    const rect = badgeEl.getBoundingClientRect();
    modal.style.top = (window.scrollY + rect.bottom + 8) + "px";
    modal.style.left = Math.max(10, window.scrollX + rect.left - 120) + "px";
    activeTooltip = modal;
  }

  function removeVisualHighlights() {
    document.querySelectorAll(".dpd-highlight-high, .dpd-highlight-medium, .dpd-highlight-low")
      .forEach(el => el.classList.remove("dpd-highlight-high", "dpd-highlight-medium", "dpd-highlight-low"));
    document.querySelectorAll(".dpd-badge").forEach(b => b.remove());
    if (activeTooltip) { activeTooltip.remove(); activeTooltip = null; }
  }

  async function runPageScan() {
    const extractedElements = extractTargetDOMElements();
    const payload = {
      url: window.location.href,
      page_title: document.title,
      text: document.body.innerText ? document.body.innerText.substring(0, 4000) : "",
      elements: extractedElements
    };
    try {
      const response = await fetch(API_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error("API scan failed.");
      const data = await response.json();
      applyVisualHighlights(data.detections || []);
      chrome.runtime.sendMessage({ type: "SCAN_RESULTS_READY", data: data });
      return data;
    } catch (err) {
      console.warn("[DPD] Scan error:", err.message);
      return null;
    }
  }

  chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
    if (req.type === "TRIGGER_SCAN") {
      runPageScan().then(data => sendResponse({ status: "SUCCESS", data }));
      return true;
    }
    if (req.type === "CLEAR_HIGHLIGHTS") {
      removeVisualHighlights();
      sendResponse({ status: "CLEARED" });
    }
  });

  window.addEventListener("load", () => {
    setTimeout(runPageScan, 1500);
  });
})();
