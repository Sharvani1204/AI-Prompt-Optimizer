"""
weakness_detector.py

Identifies areas of improvement (weaknesses) in a prompt based on
scores from prompt analysis and a configurable threshold.
"""

import logging
from typing import Dict, Any, List

# Setup logging
logger = logging.getLogger("PromptOpt.WeaknessDetector")

# Configurable default threshold
LOW_SCORE_THRESHOLD = 0.40

# Actionable feedback mapping for low scores
WEAKNESS_MAP = {
    "clarity": "Lack of clarity: Ensure the instruction is direct and free of ambiguous phrasing.",
    "context": "Lack of context: Add background information, reference data, or role/persona declarations.",
    "specificity": "Low specificity: Define boundaries, depth, or specify the target audience.",
    "intent": "Unclear intent: Clearly formulate a directive or use explicit command verbs.",
    "constraints": "No constraints specified: Set limits, boundaries, or negative instructions (what to avoid).",
    "output_format": "No output format specified: Define the desired output structure (e.g., JSON, table, list).",
    "examples": "No examples provided: Use few-shot examples or input/output templates to guide formatting."
}

def detect_weaknesses(analysis: Dict[str, Any], threshold: float = LOW_SCORE_THRESHOLD) -> List[str]:
    """
    Scans the prompt analysis dictionary and lists weaknesses for metrics below the threshold.
    
    Args:
        analysis (Dict[str, Any]): The structured analysis output from analyze_prompt.
        threshold (float): The threshold score below which a metric is marked as weak.
        
    Returns:
        List[str]: A list of weakness messages indicating areas of improvement.
        
    Raises:
        TypeError: If analysis is not a dict or threshold is not a float.
        ValueError: If analysis does not contain the "metrics" key.
    """
    # 1. Validation
    if not isinstance(analysis, dict):
        logger.error(f"Invalid analysis input type: {type(analysis)}")
        raise TypeError("Analysis input must be a dictionary.")

    if not isinstance(threshold, (int, float)):
        logger.error(f"Invalid threshold type: {type(threshold)}")
        raise TypeError("Threshold must be a numeric float/int.")

    if "metrics" not in analysis:
        logger.error("Missing 'metrics' key in analysis dict.")
        raise ValueError("Analysis dictionary must contain 'metrics' key.")

    metrics = analysis["metrics"]
    if not isinstance(metrics, dict):
        logger.error("The 'metrics' value must be a sub-dictionary.")
        raise TypeError("The 'metrics' key must map to a dictionary of metric scores.")

    logger.info(f"Scanning weaknesses with threshold: {threshold}")
    weaknesses = []

    # 2. Detecting weaknesses based on threshold
    for metric_name, score in metrics.items():
        if not isinstance(score, (int, float)):
            logger.error(f"Metric '{metric_name}' has a non-numeric score: {score}")
            raise TypeError(f"Metric '{metric_name}' must have a numeric score, got {type(score).__name__}.")
            
        if score < threshold:
            weakness_msg = WEAKNESS_MAP.get(metric_name, f"Low score for '{metric_name}': Score {score}")
            weaknesses.append(weakness_msg)
            logger.debug(f"Detected weakness: {metric_name} (Score: {score})")

    logger.info(f"Scanning complete. Found {len(weaknesses)} weakness(es).")
    return weaknesses
