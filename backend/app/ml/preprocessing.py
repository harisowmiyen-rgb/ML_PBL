import re
from bs4 import BeautifulSoup
from typing import List

CLEAN_WHITESPACE = re.compile(r"\s+")
CURRENCY_PATTERN = re.compile(r"[₹$€£¥]")

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Strip HTML if present
    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "html.parser").get_text(separator=" ")
    
    # Normalize currency
    text = CURRENCY_PATTERN.sub(" CURRENCY ", text)
    # Lowercase & normalize spaces
    text = text.lower()
    text = CLEAN_WHITESPACE.sub(" ", text).strip()
    return text

def extract_candidate_snippets(full_text: str, max_length: int = 200) -> List[str]:
    # Split text into candidate phrases/sentences for classification
    if not full_text:
        return []
    raw_sentences = re.split(r"[\n\r.!?]+", full_text)
    snippets = []
    for s in raw_sentences:
        cleaned = clean_text(s)
        if len(cleaned) > 10:
            if len(cleaned) > max_length:
                cleaned = cleaned[:max_length]
            snippets.append(cleaned)
    return snippets
