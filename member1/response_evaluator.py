"""
response_evaluator.py

Evaluates and compares the quality of the original response versus the optimized response.
Uses sentence-transformers for semantic similarity and local rule-based heuristics
(with clean interfaces for future LLM-as-a-Judge integration) for subjective axes.
"""

import logging
import re
from typing import Dict, Any, Optional

# Setup logging
logger = logging.getLogger("PromptOpt.ResponseEvaluator")

# Lazy loading variables
_model: Optional[Any] = None

# Evaluation weights (must sum to 1.0)
EVAL_WEIGHTS = {
    "relevance": 0.20,
    "accuracy": 0.20,
    "completeness": 0.20,
    "coherence": 0.15,
    "helpfulness": 0.15,
    "semantic_similarity": 0.10
}

def get_embedding_model() -> Optional[Any]:
    """Lazily loads and returns the SentenceTransformer model, or None if unavailable."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Initializing sentence-transformers model (all-MiniLM-L6-v2)...")
            _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning(f"Failed to load sentence-transformers model: {e}. "
                           "Semantic similarity will fall back to token overlap.")
            return None
    return _model

# --- SUBJECTIVE METRIC HEURISTIC PLUGINS (LLM-as-a-Judge Placeholders) ---

def score_coherence(text: str) -> float:
    """
    Heuristically estimates local text coherence.
    Looks at sentence count, sentence length consistency, and transition word density.
    """
    clean_text = text.strip().lower()
    if not clean_text:
        return 0.0

    # Split into sentences
    sentences = [s.strip() for s in re.split(r"[.!?]+", clean_text) if s.strip()]
    if not sentences:
        return 0.2

    # Reward transition words
    transitions = ["however", "therefore", "thus", "consequently", "moreover", 
                   "furthermore", "in addition", "for instance", "firstly", "finally"]
    transition_count = sum(1 for t in transitions if t in clean_text)
    
    # Calculate density
    density = transition_count / len(sentences)
    transition_bonus = min(density * 0.5, 0.2)  # up to 0.2 bonus

    # Readability/sentence structure penalty for extremely long sentence blocks
    long_sentences = sum(1 for s in sentences if len(s.split()) > 35)
    penalty = min(long_sentences * 0.1, 0.3)

    # Base score
    base_score = 0.75
    score = base_score + transition_bonus - penalty
    return round(max(0.1, min(score, 1.0)), 2)

def score_completeness(text: str) -> float:
    """
    Heuristically estimates response completeness.
    Analyzes word count and structural features like lists, markdown headers, and formatting.
    """
    clean_text = text.strip().lower()
    if not clean_text:
        return 0.0

    words = clean_text.split()
    word_count = len(words)

    # Length reward (up to 0.5) - sweet spot is 100-400 words
    if word_count < 15:
        len_score = 0.1
    elif word_count < 50:
        len_score = 0.3
    elif 100 <= word_count <= 400:
        len_score = 0.5
    else:
        len_score = 0.4  # slight penalty for excessive verbosity

    # Structure reward: list items, markdown titles, code blocks (up to 0.4)
    structure_score = 0.0
    if re.search(r"^\s*[-*+•]\s+", text, re.MULTILINE):
        structure_score += 0.15  # bullet list
    if re.search(r"^\s*\d+\.\s+", text, re.MULTILINE):
        structure_score += 0.15  # numbered list
    if "```" in text:
        structure_score += 0.1   # code block
    if "#" in text:
        structure_score += 0.1   # markdown headers

    # Content breadth heuristic (e.g., paragraph count)
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    paragraph_bonus = 0.1 if len(paragraphs) >= 2 else 0.0

    score = len_score + structure_score + paragraph_bonus
    return round(max(0.1, min(score, 1.0)), 2)

def score_helpfulness(text: str) -> float:
    """
    Heuristically estimates response helpfulness.
    Checks for actionable language, layout organization, and lack of refusal patterns.
    """
    clean_text = text.strip().lower()
    if not clean_text:
        return 0.0

    score = 0.70  # default base helpfulness for any non-empty response

    # 1. Formatting layout bonus
    if re.search(r"^\s*[-*+•\d]\s+", text, re.MULTILINE) or "```" in text or "|" in text:
        score += 0.15

    # 2. Command/instructive terms (giving instructions, tips, steps)
    instructive_terms = ["step", "tip", "note:", "important:", "guide", "how to", "ensure", "always"]
    if any(term in clean_text for term in instructive_terms):
        score += 0.10

    # 3. Refusal/error penalty
    refusals = ["i cannot", "i do not know", "as an ai", "unable to answer", "sorry, but"]
    if any(refusal in clean_text for refusal in refusals):
        score -= 0.40

    return round(max(0.1, min(score, 1.0)), 2)

def score_relevance(text: str, reference: str) -> float:
    """
    Heuristically estimates relevance.
    Evaluates term overlap and semantic coverage relative to the original response.
    """
    clean_text = text.strip().lower()
    clean_ref = reference.strip().lower()

    if not clean_text or not clean_ref:
        return 0.0

    # Token overlap check (TF-IDF equivalent simplified)
    words_text = set(re.findall(r"\b\w{3,}\b", clean_text))
    words_ref = set(re.findall(r"\b\w{3,}\b", clean_ref))
    
    if not words_ref:
        return 0.5

    overlap = words_text.intersection(words_ref)
    overlap_ratio = len(overlap) / len(words_ref)

    # Relevance remains high if they cover similar core vocab
    score = 0.60 + (overlap_ratio * 0.40)
    return round(max(0.1, min(score, 1.0)), 2)

def score_accuracy(text: str) -> float:
    """
    Provisional heuristic for accuracy.
    In local settings, semantic accuracy is unverified. This function acts as a placeholder
    to be integrated with a reference dataset validation or an LLM-as-a-Judge pipeline.
    """
    # Check basic formatting soundness and lack of repetition
    clean_text = text.strip()
    if not clean_text:
        return 0.0
    
    # Check for hallucination/looping text (same word repeated excessively)
    words = clean_text.lower().split()
    if len(words) > 10:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.3:
            return 0.3  # penalized heavily for repeating patterns

    # Return default high unverified baseline
    return 0.85

# --- CORE PUBLIC INTERFACE ---

def evaluate_response(original_response: str, optimized_response: str) -> Dict[str, Any]:
    """
    Compares the quality of the original response versus the optimized response.
    
    Args:
        original_response (str): The response text produced by the original prompt.
        optimized_response (str): The response text produced by the optimized prompt.
        
    Returns:
        Dict[str, Any]: Evaluation report including metric scores, overall score, 
            improvement delta, and the better response indicator.
            
    Raises:
        TypeError: If either response is not a string.
        ValueError: If either response is empty.
    """
    # 1. Validation
    if original_response is None or optimized_response is None:
        logger.error("Received None for response inputs.")
        raise TypeError("Responses must be strings, cannot be None.")
        
    if not isinstance(original_response, str) or not isinstance(optimized_response, str):
        logger.error("Responses must be string types.")
        raise TypeError("Responses must be string types.")

    orig_stripped = original_response.strip()
    opt_stripped = optimized_response.strip()

    if not orig_stripped or not opt_stripped:
        logger.error("Received empty response inputs.")
        raise ValueError("Responses must be non-empty strings.")

    logger.info("Starting response evaluation.")

    # 2. Semantic Similarity Calculation
    # Lazy loads the model, encodes sentences, and computes cosine similarity
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        model = get_embedding_model()
        if model is None:
            raise ImportError("SentenceTransformer model is unavailable.")
        logger.info("Computing embeddings for semantic similarity...")
        embeddings = model.encode([orig_stripped, opt_stripped])
        
        sim_matrix = cosine_similarity([embeddings[0]], [embeddings[1]])
        semantic_sim = float(sim_matrix[0][0])
        # Clip similarity score strictly between 0.0 and 1.0
        semantic_sim = float(np.clip(semantic_sim, 0.0, 1.0))
        logger.info(f"Calculated Semantic Similarity: {semantic_sim:.4f}")
    except Exception as e:
        logger.warning(f"Error computing semantic embedding similarity: {e}. Falling back to token overlap.")
        # Fallback to Jaccard-like similarity if sentence-transformers fail
        words_orig = set(orig_stripped.lower().split())
        words_opt = set(opt_stripped.lower().split())
        intersection = words_orig.intersection(words_opt)
        union = words_orig.union(words_opt)
        semantic_sim = len(intersection) / len(union) if union else 0.0

    # 3. Calculate dimension scores for both original and optimized responses
    # Subjective metrics for Original response
    relevance_orig = 1.0  # reference relevance to itself is 1.0
    accuracy_orig = score_accuracy(orig_stripped)
    completeness_orig = score_completeness(orig_stripped)
    coherence_orig = score_coherence(orig_stripped)
    helpfulness_orig = score_helpfulness(orig_stripped)
    similarity_orig = 1.0  # similarity to itself is 1.0

    # Subjective metrics for Optimized response
    relevance_opt = score_relevance(opt_stripped, orig_stripped)
    accuracy_opt = score_accuracy(opt_stripped)
    completeness_opt = score_completeness(opt_stripped)
    coherence_opt = score_coherence(opt_stripped)
    helpfulness_opt = score_helpfulness(opt_stripped)
    similarity_opt = semantic_sim

    # 4. Compute Weighted Quality Scores (0 - 100 scale)
    def compute_weighted_score(rel, acc, comp, coh, help_val, sim) -> float:
        score = (
            rel * EVAL_WEIGHTS["relevance"] +
            acc * EVAL_WEIGHTS["accuracy"] +
            comp * EVAL_WEIGHTS["completeness"] +
            coh * EVAL_WEIGHTS["coherence"] +
            help_val * EVAL_WEIGHTS["helpfulness"] +
            sim * EVAL_WEIGHTS["semantic_similarity"]
        )
        return round(score * 100.0, 2)

    score_orig = compute_weighted_score(
        relevance_orig, accuracy_orig, completeness_orig, 
        coherence_orig, helpfulness_orig, similarity_orig
    )
    score_opt = compute_weighted_score(
        relevance_opt, accuracy_opt, completeness_opt, 
        coherence_opt, helpfulness_opt, similarity_opt
    )

    improvement = round(score_opt - score_orig, 2)

    # 5. Decide better response
    # We allow a small threshold (e.g. 0.5 points) for similarity range
    if improvement > 0.50:
        better_response = "optimized"
    elif improvement < -0.50:
        better_response = "original"
    else:
        better_response = "similar"

    logger.info(f"Evaluation finished. Original Score: {score_orig}, Optimized Score: {score_opt}, Better: {better_response}")

    # Return structured dict focusing on optimized response metrics and comparing with original
    return {
        "metrics": {
            "relevance": round(relevance_opt, 2),
            "accuracy": round(accuracy_opt, 2),
            "completeness": round(completeness_opt, 2),
            "coherence": round(coherence_opt, 2),
            "helpfulness": round(helpfulness_opt, 2),
            "semantic_similarity": round(semantic_sim, 2)
        },
        "overall_score": int(round(score_opt)),
        "improvement": improvement,
        "better_response": better_response
    }
