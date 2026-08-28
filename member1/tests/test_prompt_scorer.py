"""
test_prompt_scorer.py

Unit tests for prompt_scorer.py.
"""

import pytest
from member1 import calculate_prompt_score

def test_calculate_prompt_score_standard():
    analysis = {
        "metrics": {
            "clarity": 1.0,
            "context": 1.0,
            "specificity": 1.0,
            "intent": 1.0,
            "constraints": 1.0,
            "output_format": 1.0,
            "examples": 1.0
        }
    }
    
    # Perfect prompt should score 100 with Excellent grade
    result = calculate_prompt_score(analysis)
    assert result["score"] == 100.0
    assert result["score_100"] == 100
    assert result["grade"] == "Excellent"
    
    # Worst prompt should score 0 with Poor grade
    analysis_worst = {
        "metrics": {
            "clarity": 0.0,
            "context": 0.0,
            "specificity": 0.0,
            "intent": 0.0,
            "constraints": 0.0,
            "output_format": 0.0,
            "examples": 0.0
        }
    }
    result_worst = calculate_prompt_score(analysis_worst)
    assert result_worst["score"] == 0.0
    assert result_worst["score_100"] == 0
    assert result_worst["grade"] == "Poor"

def test_calculate_prompt_score_custom_weights():
    analysis = {
        "metrics": {
            "clarity": 1.0,
            "context": 0.0,
            "specificity": 0.0,
            "intent": 0.0,
            "constraints": 0.0,
            "output_format": 0.0,
            "examples": 0.0
        }
    }
    
    # Standard score: clarity is 20% weight, so score is 20.0
    res_std = calculate_prompt_score(analysis)
    assert res_std["score"] == 20.0
    assert res_std["grade"] == "Poor"
    
    # Custom weights: give clarity 100% (1.0) and others 0.0
    custom_weights = {
        "clarity": 1.0,
        "context": 0.0,
        "specificity": 0.0,
        "intent": 0.0,
        "constraints": 0.0,
        "output_format": 0.0,
        "examples": 0.0
    }
    
    res_custom = calculate_prompt_score(analysis, custom_weights=custom_weights)
    assert res_custom["score"] == 100.0
    assert res_custom["grade"] == "Excellent"

def test_calculate_prompt_score_weight_validation():
    analysis = {"metrics": {"clarity": 1.0, "context": 1.0, "specificity": 1.0, "intent": 1.0, "constraints": 1.0, "output_format": 1.0, "examples": 1.0}}
    
    # Weights must sum to 1.0 (invalid sum)
    invalid_weights = {
        "clarity": 0.5,
        "context": 0.1,
        "specificity": 0.1,
        "intent": 0.1,
        "constraints": 0.1,
        "output_format": 0.1,
        "examples": 0.1
    } # sum = 1.1
    
    with pytest.raises(ValueError):
        calculate_prompt_score(analysis, custom_weights=invalid_weights)
        
    # Weights missing keys
    missing_keys_weights = {
        "clarity": 1.0
    }
    with pytest.raises(ValueError):
        calculate_prompt_score(analysis, custom_weights=missing_keys_weights)

def test_calculate_prompt_score_invalid_inputs():
    with pytest.raises(TypeError):
        calculate_prompt_score("not a dict")
        
    with pytest.raises(ValueError):
        calculate_prompt_score({"prompt": "no metrics"})
        
    with pytest.raises(TypeError):
        calculate_prompt_score({"metrics": "not a dict"})
