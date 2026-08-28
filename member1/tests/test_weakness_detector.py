"""
test_weakness_detector.py

Unit tests for weakness_detector.py.
"""

import pytest
from member1 import detect_weaknesses

def test_detect_weaknesses_standard():
    # Construct a mock analysis dictionary
    analysis = {
        "prompt": "Test prompt",
        "metrics": {
            "clarity": 0.8,
            "context": 0.1,  # Below threshold 0.4
            "specificity": 0.2,  # Below threshold 0.4
            "intent": 0.9,
            "constraints": 0.0,  # Below threshold 0.4
            "output_format": 0.0,  # Below threshold 0.4
            "examples": 0.0  # Below threshold 0.4
        }
    }
    
    weaknesses = detect_weaknesses(analysis)
    
    # 5 metrics are below 0.40
    assert len(weaknesses) == 5
    
    # Verify specific warning triggers are included
    assert any("context" in w.lower() for w in weaknesses)
    assert any("specificity" in w.lower() for w in weaknesses)
    assert any("constraints" in w.lower() for w in weaknesses)
    assert any("format" in w.lower() for w in weaknesses)
    assert any("examples" in w.lower() for w in weaknesses)
    
    # Clarity and intent should not be flagged as weaknesses
    assert not any("clarity" in w.lower() for w in weaknesses)
    assert not any("intent" in w.lower() for w in weaknesses)

def test_detect_weaknesses_custom_threshold():
    analysis = {
        "prompt": "Test prompt",
        "metrics": {
            "clarity": 0.8,
            "context": 0.5,
            "specificity": 0.5,
            "intent": 0.9,
            "constraints": 0.5,
            "output_format": 0.5,
            "examples": 0.5
        }
    }
    
    # At default threshold 0.40, no weaknesses should be detected
    assert len(detect_weaknesses(analysis)) == 0
    
    # If threshold is bumped to 0.60, 5 metrics are flagged
    weaknesses_high = detect_weaknesses(analysis, threshold=0.60)
    assert len(weaknesses_high) == 5

def test_detect_weaknesses_validation():
    # Type validation
    with pytest.raises(TypeError):
        detect_weaknesses("not a dict")
        
    with pytest.raises(TypeError):
        detect_weaknesses({"metrics": {}}, threshold="high")
        
    # Value validation: missing metrics
    with pytest.raises(ValueError):
        detect_weaknesses({"prompt": "No metrics"})
        
    # Value validation: non-dict metrics
    with pytest.raises(TypeError):
        detect_weaknesses({"metrics": "not a dict"})
