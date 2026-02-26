"""
tfidf_utils.py — TF-IDF based structural similarity for plagiarism Stage 1.
Fast local computation — no external API calls.
"""

import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def compute_tfidf_similarity(
    new_text: str, existing_texts: List[str]
) -> Tuple[float, int]:
    """
    Compare new_text against a list of existing submission texts using TF-IDF.

    Returns:
        (max_similarity_score, index_of_best_match)
        Returns (0.0, -1) if existing_texts is empty or all empty strings.
    """
    if not existing_texts:
        return 0.0, -1

    # Filter out empties but keep track of original indices
    indexed = [(i, t) for i, t in enumerate(existing_texts) if t and t.strip()]
    if not indexed:
        return 0.0, -1

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        original_indices = [i for i, _ in indexed]
        texts = [new_text] + [t for _, t in indexed]

        vectorizer = TfidfVectorizer(
            min_df=1,
            max_features=10000,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        tfidf_matrix = vectorizer.fit_transform(texts)

        # new_text is at index 0; compare against all others
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        best_local_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_local_idx])
        best_original_idx = original_indices[best_local_idx]

        logger.info(f"TF-IDF max similarity: {best_score:.3f} (vs. submission idx {best_original_idx})")
        return round(best_score, 4), best_original_idx

    except Exception as e:
        logger.error(f"TF-IDF similarity error: {e}")
        return 0.0, -1
