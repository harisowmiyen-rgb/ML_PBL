# Dark Pattern Detector for E-Commerce

A full-stack, production-style AI system that detects deceptive, coercive, and manipulative UI/UX patterns (Dark Patterns) on e-commerce websites in real time. It features a Chrome Manifest V3 extension backed by a hybrid FastAPI backend, combining heuristic rule-based detection with machine learning text classification (DistilBERT / NLP), an automated DOM element highlighter, PostgreSQL storage, and user feedback reporting.

---

## 1. Problem Statement & Overview

Dark patterns are user interfaces meticulously designed to trick, coerce, or manipulate consumers into making choices they would not otherwise make—such as buying unwanted subscriptions, paying hidden surcharges, rushing into purchases due to manufactured urgency, or feeling guilt-tripped into consenting to privacy intrusion.

This project delivers an end-to-end protective shield that:
1. Automatically inspects web pages for high-risk elements (ticking countdown timers, hidden fees, false stock counters, confirmshaming decline options, preselected checkboxes).
2. Uses an NLP text classification engine and rule heuristics to classify manipulative text.
3. Overlays visual warning badges and interactive explanatory modals directly on the webpage.
4. Generates comprehensive audit reports, risk scores (0–100), and maintains scan history.

---

## 2. System Architecture

```
+-----------------------------------------------------------------------------------+
|                            E-Commerce Web Page (DOM)                             |
+-----------------------------------------------------------------------------------+
       |                                                              ▲
       | 1. Dynamic DOM Inspection & MutationObserver                  | In-Page Badges &
       ▼                                                              | Explanatory Modals
+------------------------------------+                                |
| Chrome Manifest V3 Extension       |                                |
| - content.js (DOM Scanner)         |                                |
| - background.js (Service Worker)   |                                |
| - popup.html/js (Dashboard)        |                                |
+------------------------------------+                                |
       |                                                              |
       | 2. POST /api/scan (JSON Payload: text elements, selectors, context)
       ▼                                                              |
+---------------------------------------------------------------------+-------------+
| FastAPI High-Performance Backend Service (Port 8000)                               |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | Request Validation & HTML Sanitization (Pydantic v2 + BeautifulSoup4)       |  |
|  +-----------------------------------------------------------------------------+  |
|                                     |                                             |
|        +----------------------------+----------------------------+                |
|        ▼                                                         ▼                |
|  +----------------------------------+             +----------------------------+  |
|  | Heuristic Rule Engine            |             | ML / NLP Pipeline          |  |
|  | - Urgency Regex & Timers         |             | - DistilBERT Classifier    |  |
|  | - Scarcity & Social Proof Cues   |             | - Calibrated NLP Pipeline  |  |
|  | - Hidden Costs & Drip Pricing    |             | - Confidence Thresholding  |  |
|  | - Trick Questions & Negation     |             | - Preprocessing & Cleanup  |  |
|  +----------------------------------+             +----------------------------+  |
|        |                                                         |                |
|        +----------------------------+----------------------------+                |
|                                     ▼                                             |
|  +-----------------------------------------------------------------------------+  |
|  | Prediction Fusion Engine & Weighted Scoring                                 |  |
|  | Combined Confidence = (0.60 * ML) + (0.40 * Rule)                           |  |
|  | Risk Score: Heuristic Impact Weighting [0 - 100]                            |  |
|  +-----------------------------------------------------------------------------+  |
|                                     |                                             |
|        +----------------------------+----------------------------+                |
|        ▼                                                         ▼                |
|  +----------------------------------+             +----------------------------+  |
|  | Storage & Persistence Layer      |             | API Response Serialization |  |
|  | PostgreSQL (SQLAlchemy ORM)      |             | JSON Schema with           |  |
|  | Scans, Detections, User Feedback |             | Detections, Risk, Reasons  |  |
|  +----------------------------------+             +----------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 3. Dark Pattern Taxonomy & Risk Scoring

### Classification Categories:
- **0: Normal** — Legitimate e-commerce content, specs, prices, and standard policies.
- **1: Fake Urgency** — False countdown timers and fabricated expiration limits pressuring immediate action.
- **2: Scarcity** — Artificial stock counters ("Only 1 left in stock!") prompting fear of missing out.
- **3: Hidden Cost** — Unbundled ancillary fees (drip pricing) revealed only at final checkout.
- **4: Trick Question** — Mismatched double negatives in checkboxes to induce accidental consent.
- **5: Confirmshaming** — Emotionally manipulative or guilt-tripping decline buttons ("No thanks, I hate saving").
- **6: Sneak Into Basket** — Unsolicited add-ons, warranties, or donations auto-added to cart.
- **7: Forced Continuity** — Free trials rolling into auto-renewing charges with obfuscated cancellation.
- **8: Disguised Advertisement** — Sponsored promotional links styled identically to organic recommendations.
- **9: Social Proof Manipulation** — Fabricated viewer or buyer activity claims ("24 people viewing this").
- **10: Preselected Option** — Default pre-ticked checkboxes for recurring subscriptions or insurance.
- **11: Misleading Information** — Deceptive struck-through baseline anchor prices never actually charged.

### Risk Score Formula:
$$\text{Total Risk} = \sum (\text{Pattern Weight} \times \text{Confidence})$$
- Fake Urgency: 30 pts
- Hidden Cost: 30 pts
- Trick Question: 20 pts
- Confirmshaming: 20 pts
- Scarcity: 10 pts
- Other Categories: 10–25 pts
- Normalized Range: **0–29 Low Risk** (Green), **30–59 Medium Risk** (Amber), **60–100 High Risk** (Red).

---

## 4. Quick Start & Installation

### Prerequisites:
- Python 3.10+ (Tested on Python 3.11.9)
- Google Chrome or Chromium-based browser (Edge, Brave)
- Docker & Docker Compose (Optional for containerized deployment)

### Local Setup:

1. **Activate Virtual Environment & Install Dependencies:**
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
# source venv/bin/activate # On Linux/macOS
pip install -r backend/requirements.txt
```

2. **Train and Persist ML Model:**
```bash
python ml/train.py
python ml/evaluate.py
python ml/save_model.py
```

3. **Start the FastAPI Backend Server:**
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
The server will start on `http://127.0.0.1:8000`.
- API Root: `http://127.0.0.1:8000/`
- Interactive OpenAPI Documentation: `http://127.0.0.1:8000/docs`
- Redoc Documentation: `http://127.0.0.1:8000/redoc`

4. **Install the Chrome Extension:**
- Open Google Chrome and navigate to `chrome://extensions/`.
- Enable **Developer mode** (toggle in upper right).
- Click **Load unpacked**.
- Select the `extension/` folder inside this repository.
- The Dark Pattern Detector shield icon will appear in your Chrome toolbar!

5. **Test Live with the Demo E-Commerce Store:**
- Open `demo/ecommerce_test_page.html` in Chrome.
- Click the Dark Pattern Detector extension icon in the toolbar.
- Click **Scan Page**.
- Notice the in-page red dashed borders, warning badges, countdown timer alerts, and interactive explanation tooltips!

---

## 5. API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API status and root greeting |
| `GET` | `/api/health` | Healthcheck and service info |
| `POST` | `/api/scan` | Analyzes page DOM elements or text; returns risk score & detections |
| `GET` | `/api/reports` | Retrieves recent scan history |
| `GET` | `/api/reports/{id}`| Retrieves full detection details for a specific scan |
| `POST` | `/api/feedback` | Records user feedback (Correct / False Alarm) for retraining |

---

## 6. Running Tests

Execute the automated test suite covering detectors, ML pipeline, and API endpoints:
```bash
pytest -v tests/
```

---

## 7. Docker Deployment

To launch the complete production stack (FastAPI Backend + PostgreSQL Database) with one command:
```bash
docker compose up -d --build
```
