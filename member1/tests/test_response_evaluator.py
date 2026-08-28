"""
test_response_evaluator.py

Unit tests for response_evaluator.py.
"""

import pytest
from member1 import evaluate_response

def test_evaluate_response_identical():
    resp = "This is a standard machine learning response with multiple sentences and list items."
    
    # Evaluate identical responses
    result = evaluate_response(resp, resp)
    
    # Check structure
    assert isinstance(result, dict)
    assert "metrics" in result
    assert "overall_score" in result
    assert "improvement" in result
    assert "better_response" in result
    
    # Identical responses must have 1.0 semantic similarity and ~0 improvement
    assert result["metrics"]["semantic_similarity"] == 1.0
    assert result["improvement"] == 0.0
    assert result["better_response"] == "similar"

def test_evaluate_response_improvement():
    original = "Computers learn from data. That's ML."
    
    # Optimized has structure, formatting, lists, notes, and transition words (higher coherence/completeness)
    optimized = (
        "### Introduction to Machine Learning\n\n"
        "Machine learning (ML) is an advanced computer science discipline where systems learn from historical data.\n\n"
        "#### Crucial Types:\n"
        "- **Supervised learning**: Learned from labeled targets.\n"
        "- **Unsupervised learning**: Discovers hidden structures in unlabeled clusters.\n\n"
        "Therefore, choosing the correct model is vital for performance. Always clean your data."
    )
    
    result = evaluate_response(original, optimized)
    
    # The optimized response should score higher and be marked as better
    assert result["improvement"] > 0.0
    assert result["better_response"] == "optimized"
    
    # Semantic similarity should be less than 1.0 (they are different)
    assert 0.0 <= result["metrics"]["semantic_similarity"] < 1.0

def test_evaluate_response_validation():
    # Test type errors
    with pytest.raises(TypeError):
        evaluate_response(None, "Valid response")
        
    with pytest.raises(TypeError):
        evaluate_response("Valid response", 123)
        
    # Test value errors
    with pytest.raises(ValueError):
        evaluate_response("", "Valid response")
        
    with pytest.raises(ValueError):
        evaluate_response("Valid response", "  \n  ")
