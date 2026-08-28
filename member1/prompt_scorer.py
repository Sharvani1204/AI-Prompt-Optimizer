"""
prompt_scorer.py

Calculates the overall prompt quality score using a weighted sum model
and maps it to qualitative grades.
"""

import logging
from typing import Dict, Any, Optional, Tuple

# Setup logging
logger = logging.getLogger("PromptOpt.PromptScorer")

# Initial research weights (must sum to 1.0)
DEFAULT_WEIGHTS = {
    "clarity": 0.20,
    "context": 0.15,
    "specificity": 0.20,
    "intent": 0.15,
    "constraints": 0.10,
    "output_format": 0.10,
    "examples": 0.10
}

# Qualitative grading scale
DEFAULT_GRADING_SCALE = {
    "Excellent": (90, 100),
    "Good": (75, 89),
    "Fair": (60, 74),
    "Weak": (40, 59),
    "Poor": (0, 39)
}

def get_grade(score_100: int, grading_scale: Dict[str, Tuple[int, int]] = DEFAULT_GRADING_SCALE) -> str:
    """Maps a 0-100 score to a qualitative grade based on the grading scale."""
    for grade, (low, high) in grading_scale.items():
        if low <= score_100 <= high:
            return grade
    # Fallback in case of rounding edge cases
    if score_100 > 100:
        return "Excellent"
    return "Poor"

def calculate_prompt_score(
    analysis: Dict[str, Any], 
    custom_weights: Optional[Dict[str, float]] = None,
    grading_scale: Optional[Dict[str, Tuple[int, int]]] = None
) -> Dict[str, Any]:
    """
    Calculates a weighted quality score from prompt analysis metrics.
    
    Args:
        analysis (Dict[str, Any]): Prompt analysis dictionary from analyze_prompt.
        custom_weights (Dict[str, float], optional): Dictionary of weights. 
            If None, uses DEFAULT_WEIGHTS.
        grading_scale (Dict[str, tuple], optional): Dictionary of grade boundaries.
            If None, uses DEFAULT_GRADING_SCALE.
            
    Returns:
        Dict[str, Any]: Quality score breakdown containing float score, 
            score_100 integer, letter grade, and the weights used.
            
    Raises:
        TypeError: If input analysis or weights are not dictionaries.
        ValueError: If weights do not sum to 1.0, or metrics keys are missing.
    """
    # 1. Validation of analysis input
    if not isinstance(analysis, dict):
        logger.error(f"Invalid analysis input type: {type(analysis)}")
        raise TypeError("Analysis input must be a dictionary.")

    if "metrics" not in analysis:
        logger.error("Missing 'metrics' key in analysis dict.")
        raise ValueError("Analysis dictionary must contain 'metrics' key.")

    metrics = analysis["metrics"]
    if not isinstance(metrics, dict):
        logger.error("The 'metrics' value must be a dictionary.")
        raise TypeError("The 'metrics' key must map to a dictionary of metric scores.")

    # 2. Weights setup and validation
    weights = custom_weights if custom_weights is not None else DEFAULT_WEIGHTS
    if not isinstance(weights, dict):
        logger.error(f"Invalid weights type: {type(weights)}")
        raise TypeError("Weights must be a dictionary.")

    # Verify keys match
    required_keys = set(DEFAULT_WEIGHTS.keys())
    provided_keys = set(weights.keys())
    missing_keys = required_keys - provided_keys
    if missing_keys:
        logger.error(f"Weights dictionary is missing keys: {missing_keys}")
        raise ValueError(f"Weights dictionary is missing keys: {missing_keys}")

    # Check sum of weights
    weights_sum = sum(weights.values())
    if not (0.99999 <= weights_sum <= 1.00001):  # allowance for float precision
        logger.error(f"Weights sum is {weights_sum}, must be exactly 1.0.")
        raise ValueError(f"Prompt scoring weights must sum to exactly 1.0 (got {weights_sum}).")

    # 3. Calculate score
    weighted_sum = 0.0
    for metric_name, weight in weights.items():
        score = metrics.get(metric_name)
        if score is None:
            logger.error(f"Metric '{metric_name}' is missing in analysis output.")
            raise ValueError(f"Analysis metrics is missing required key '{metric_name}'.")
        if not isinstance(score, (int, float)):
            logger.error(f"Metric '{metric_name}' score must be numeric (got {type(score).__name__}).")
            raise TypeError(f"Metric '{metric_name}' score must be numeric.")
            
        weighted_sum += weight * score

    # Scale score to 0 - 100
    score_float = round(weighted_sum * 100.0, 2)
    score_int = int(round(score_float))

    # 4. Grading
    scale = grading_scale if grading_scale is not None else DEFAULT_GRADING_SCALE
    grade = get_grade(score_int, scale)

    logger.info(f"Calculated prompt score: {score_float}/100, Grade: {grade}")

    return {
        "score": score_float,
        "score_100": score_int,
        "grade": grade,
        "weights": weights
    }
