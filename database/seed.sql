-- Sample Seed Data for Dark Pattern Detector

INSERT INTO users (username, email, password_hash)
VALUES ('admin', 'admin@darkpatterndetector.local', '$2b$12$e8Y6bFpL1pL7xW4k8yF1keZgIuE6nL.dD6/zI3cQ6a2P7z4C5oZKy')
ON CONFLICT (username) DO NOTHING;

INSERT INTO scans (user_id, url, page_title, scan_time, overall_risk_score, total_patterns_detected)
VALUES (1, 'https://example-shop.com/product/deals', 'Ultra Fast Mega Deals - Shoes & Apparel', CURRENT_TIMESTAMP, 78.5, 3);

INSERT INTO detections (scan_id, pattern_type, confidence, detected_text, explanation, severity, html_selector)
VALUES 
(1, 'Fake Urgency', 0.94, 'Hurry! Only 02:45 minutes left before this deal expires!', 'Countdown timer tied to immediate transaction pressure.', 'High', '#deal-countdown-banner'),
(1, 'Scarcity', 0.86, 'Only 2 items left in stock - 18 people have this in their cart', 'Artificially stimulated fear of missing out via dynamic stock counter.', 'High', '.stock-scarcity-alert'),
(1, 'Hidden Cost', 0.72, 'Discreet mandatory handling charge ₹199 added at payment', 'Drip pricing fee not disclosed on main product listing.', 'Medium', '.cart-summary .hidden-fee');

INSERT INTO feedback (detection_id, user_feedback)
VALUES (1, 'Correct'), (2, 'Correct');

INSERT INTO model_predictions (detection_id, model_name, confidence, predicted_class)
VALUES 
(1, 'DistilBERT-DarkPatterns', 0.94, 'Fake Urgency'),
(2, 'DistilBERT-DarkPatterns', 0.86, 'Scarcity'),
(3, 'DistilBERT-DarkPatterns', 0.72, 'Hidden Cost');
