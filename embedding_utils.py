"""
embedding_utils.py — OpenAI embedding-based semantic similarity for plagiarism Stage 2.
Handles long documents via chunking and averaging.
"""

import os
import logging
import numpy as np
from typing import List, Optional

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
MAX_TOKENS_PER_CHUNK = 7500   # conservative limit under 8192 token max
APPROX_CHARS_PER_TOKEN = 4    # rough estimate


def _chunk_text(text: str, max_chars: int = MAX_TOKENS_PER_CHUNK * APPROX_CHARS_PER_TOKEN) -> List[str]:
    """Split text into chunks that fit within the token limit."""
    if len(text) <= max_chars:
        return [text]
    chunks = []
    while text:
        chunks.append(text[:max_chars])
        text = text[max_chars:]
    return chunks


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate an OpenAI embedding for the given text.
    For long texts, chunks and averages the embeddings.
    Returns None on failure.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not set in environment.")
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        chunks = _chunk_text(text)
        chunk_embeddings = []

        for chunk in chunks:
            if not chunk.strip():
                continue
            response = client.embeddings.create(model=EMBEDDING_MODEL, input=chunk)
            emb = response.data[0].embedding
            chunk_embeddings.append(emb)

        if not chunk_embeddings:
            return None

        # Average embeddings if multiple chunks
        avg_embedding = np.mean(chunk_embeddings, axis=0).tolist()
        return avg_embedding

    except Exception as e:
        logger.error(f"OpenAI embedding generation failed: {e}")
        return None


def cosine_similarity_embeddings(emb1: List[float], emb2: List[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    try:
        v1 = np.array(emb1, dtype=np.float32)
        v2 = np.array(emb2, dtype=np.float32)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (norm1 * norm2))
    except Exception as e:
        logger.error(f"Cosine similarity computation failed: {e}")
        return 0.0


def find_best_semantic_match(
    new_embedding: List[float],
    stored_submissions: List[dict],   # each dict must have 'student_id' + 'embedding'
) -> tuple[float, Optional[str]]:
    """
    Compare new_embedding against all stored submission embeddings.
    Returns (best_score, matched_student_id).
    """
    best_score = 0.0
    matched_student_id = None

    for sub in stored_submissions:
        stored_emb = sub.get("embedding")
        if not stored_emb or not isinstance(stored_emb, list):
            continue
        score = cosine_similarity_embeddings(new_embedding, stored_emb)
        if score > best_score:
            best_score = score
            matched_student_id = sub.get("student_id")

    return round(best_score, 4), matched_student_id
