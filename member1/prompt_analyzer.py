"""
prompt_analyzer.py

Analyzes an input prompt and returns scores for clarity, context, 
specificity, intent, constraints, format, and examples.
"""

import logging
from typing import Dict, Any

from member1.metrics import (
    calculate_clarity,
    calculate_context,
    calculate_specificity,
    calculate_intent,
    calculate_constraints,
    calculate_output_format,
    calculate_examples
)

# Setup logging
logger = logging.getLogger("PromptOpt.PromptAnalyzer")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Configurable limits
MAX_PROMPT_LENGTH = 50000

def analyze_prompt(prompt: str) -> Dict[str, Any]:
    """
    Analyzes the quality of a prompt based on 7 dimensions.
    
    Args:
        prompt (str): The prompt text to analyze.
        
    Returns:
        Dict[str, Any]: A dictionary containing the input prompt and metric scores.
        
    Raises:
        TypeError: If the prompt is not a string.
        ValueError: If the prompt is empty or exceeds the maximum length.
    """
    # 1. Type validation
    if prompt is None:
        logger.error("Received None for prompt input.")
        raise TypeError("Prompt must be a string, cannot be None.")
        
    if not isinstance(prompt, str):
        logger.error(f"Received invalid type {type(prompt)} for prompt input.")
        raise TypeError(f"Prompt must be a string, got {type(prompt).__name__}.")

    # 2. Value validation
    stripped_prompt = prompt.strip()
    if not stripped_prompt:
        logger.error("Received empty prompt input.")
        raise ValueError("Prompt must be a non-empty string.")

    if len(prompt) > MAX_PROMPT_LENGTH:
        logger.error(f"Prompt length {len(prompt)} exceeds limit {MAX_PROMPT_LENGTH}.")
        raise ValueError(f"Prompt exceeds the maximum allowed length of {MAX_PROMPT_LENGTH} characters.")

    logger.info(f"Analyzing prompt (length: {len(prompt)} characters).")

    # 3. Running heuristics
    metrics = {
        "clarity": calculate_clarity(stripped_prompt),
        "context": calculate_context(stripped_prompt),
        "specificity": calculate_specificity(stripped_prompt),
        "intent": calculate_intent(stripped_prompt),
        "constraints": calculate_constraints(stripped_prompt),
        "output_format": calculate_output_format(stripped_prompt),
        "examples": calculate_examples(stripped_prompt)
    }

    # 4. Assembling response structure
    result = {
        "prompt": prompt,
        "metrics": metrics
    }

    logger.info("Prompt analysis completed successfully.")
    return result
