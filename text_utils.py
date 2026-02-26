"""
text_utils.py — Text extraction and preprocessing for plagiarism checker.
Supports PDF (pdfplumber) and DOCX (python-docx).
"""

import re
import io
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n".join(pages)
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes using python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Detect file type from filename and extract text accordingly.
    Returns empty string on failure.
    """
    name_lower = filename.lower()
    if name_lower.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif name_lower.endswith(".docx") or name_lower.endswith(".doc"):
        text = extract_text_from_docx(file_bytes)
    else:
        logger.warning(f"Unsupported file type: {filename}")
        return ""

    if not text.strip():
        logger.warning(f"No text extracted from {filename}")
    return text


def preprocess_text(text: str) -> str:
    """
    Normalize text for comparison:
    - lowercase
    - remove punctuation
    - normalize whitespace
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text)        # collapse whitespace
    return text.strip()
