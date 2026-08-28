"""
test_prompt_analyzer.py

Unit tests for prompt_analyzer.py.
"""

import pytest
from member1 import analyze_prompt

def test_analyze_prompt_valid():
    prompt = "Explain machine learning in a table format."
    result = analyze_prompt(prompt)
    
    # Check structure
    assert isinstance(result, dict)
    assert "prompt" in result
    assert "metrics" in result
    assert result["prompt"] == prompt
    
    # Check metrics
    metrics = result["metrics"]
    assert isinstance(metrics, dict)
    
    required_keys = {"clarity", "context", "specificity", "intent", "constraints", "output_format", "examples"}
    assert set(metrics.keys()) == required_keys
    
    for val in metrics.values():
        assert isinstance(val, float)
        assert 0.0 <= val <= 1.0

def test_analyze_prompt_type_errors():
    # Test None
    with pytest.raises(TypeError):
        analyze_prompt(None)
        
    # Test invalid type
    with pytest.raises(TypeError):
        analyze_prompt(123)
        
    with pytest.raises(TypeError):
        analyze_prompt(["Explain this"])

def test_analyze_prompt_value_errors():
    # Test empty prompt
    with pytest.raises(ValueError):
        analyze_prompt("")
        
    # Test whitespace prompt
    with pytest.raises(ValueError):
        analyze_prompt("   \n \t  ")

def test_analyze_prompt_extreme_length():
    # Test prompt exceeding MAX_PROMPT_LENGTH (50,000 characters)
    very_long_prompt = "A" * 50001
    with pytest.raises(ValueError):
        analyze_prompt(very_long_prompt)

def test_analyze_prompt_specific_heuristics():
    # Simple prompt should get lower score on format and examples
    simple_prompt = "Explain recursion."
    res = analyze_prompt(simple_prompt)
    assert res["metrics"]["output_format"] == 0.0
    assert res["metrics"]["examples"] == 0.0

    # Prompt with format keyword should get non-zero output_format score
    formatted_prompt = "Explain recursion. Format as JSON."
    res2 = analyze_prompt(formatted_prompt)
    assert res2["metrics"]["output_format"] > 0.0
