"""
metrics.py

Provides explainable, heuristic scoring functions for prompt evaluation.
Each metric returns a normalized score in the range [0.0, 1.0].
"""

import re
from typing import Dict, Any

# Lists of patterns and keywords for heuristic analysis
ACTION_VERBS = [
    "explain", "summarize", "write", "classify", "analyze", "detect", "evaluate", 
    "translate", "generate", "create", "list", "compare", "describe", "predict", 
    "optimize", "find", "calculate", "extract", "formulate", "rewrite", "critique",
    "design", "implement", "develop", "interpret", "define", "outline", "categorize"
]

AMBIGUITY_KEYWORDS = [
    "stuff", "thing", "somewhat", "like", "etc", "something", "maybe", 
    "probably", "somehow", "whoever", "whatever", "sometime", "appropriate",
    "adequate", "good enough", "should probably"
]

ROLE_KEYWORDS = [
    r"\bact as\b", r"\byou are\b", r"\bas a\b", r"\brole\b", r"\bpersona\b",
    r"\bexpert\b", r"\bspecialist\b", r"\bprofessional\b"
]

CONTEXT_KEYWORDS = [
    r"\bcontext\b", r"\bbackground\b", r"\bgiven that\b", r"\bsuppose\b", 
    r"\bscenario\b", r"\bsituation\b", r"\bhere is\b", r"\bthe following\b"
]

DEPTH_KEYWORDS = [
    "detailed", "in-depth", "brief", "concise", "step-by-step", "comprehensive", 
    "thoroughly", "summary", "elaborate", "exhaustive", "short", "deep dive"
]

AUDIENCE_KEYWORDS = [
    r"\bfor beginners\b", r"\bfor kids\b", r"\bexpert level\b", r"\bacademic\b",
    r"\btechnical audience\b", r"\blayman\b", r"\bnon-technical\b"
]

LIMIT_KEYWORDS = [
    "words", "characters", "sentences", "paragraphs", "lines", "pages", 
    "limit", "maximum", "minimum", "no more than", "under", "exceed", "length"
]

NEGATIVE_CONSTRAINTS = [
    r"\bdo not\b", r"\bavoid\b", r"\bnever\b", r"\bshould not\b", 
    r"\bwithout\b", r"\bexclude\b", r"\bno\b", r"\brefrain\b"
]

FORMAT_KEYWORDS = [
    "json", "csv", "xml", "yaml", "table", "bullet points", "numbered list", 
    "markdown", "html", "code block", "paragraphs", "list", "summary", 
    "report", "format", "layout", "structure"
]

EXAMPLE_KEYWORDS = [
    r"\bexample\b", r"\bfor instance\b", r"\be\.g\.\b", r"\bsample\b", 
    r"\bdemonstration\b", r"\billustration\b", r"\binput:\b", r"\boutput:\b",
    r"\bq:\b", r"\ba:\b"
]

def calculate_clarity(prompt: str) -> float:
    """
    Evaluates prompt clarity based on readability, sentence structure, 
    presence of action/command verbs, and absence of ambiguity.
    """
    clean_prompt = prompt.strip().lower()
    if not clean_prompt:
        return 0.0

    # 1. Action verb presence (up to 0.4)
    has_action = any(verb in clean_prompt for verb in ACTION_VERBS)
    action_score = 0.4 if has_action else 0.0

    # 2. Sentence structure suitability (up to 0.3)
    # Sweet spot is 10-30 words. Extremely short prompts get penalized.
    words = clean_prompt.split()
    word_count = len(words)
    if 10 <= word_count <= 30:
        structure_score = 0.3
    elif 5 <= word_count < 10:
        structure_score = 0.15
    elif 30 < word_count <= 60:
        structure_score = 0.2
    else:  # Either extremely short (<5 words) or overly long (>60 words in a single block without structure)
        structure_score = 0.05

    # 3. Absence of ambiguity keywords (up to 0.3)
    ambiguity_count = sum(1 for keyword in AMBIGUITY_KEYWORDS if keyword in clean_prompt)
    if ambiguity_count == 0:
        ambiguity_score = 0.3
    elif ambiguity_count == 1:
        ambiguity_score = 0.15
    else:
        ambiguity_score = 0.0

    return round(action_score + structure_score + ambiguity_score, 2)

def calculate_context(prompt: str) -> float:
    """
    Checks if context is provided, such as background, role/persona, 
    or reference materials.
    """
    clean_prompt = prompt.strip().lower()
    if not clean_prompt:
        return 0.0

    score = 0.0

    # 1. Role / Persona indicators (up to 0.4)
    if any(re.search(pattern, clean_prompt) for pattern in ROLE_KEYWORDS):
        score += 0.4

    # 2. Context keywords (up to 0.3)
    if any(re.search(pattern, clean_prompt) for pattern in CONTEXT_KEYWORDS):
        score += 0.3

    # 3. Input placeholders or structured brackets (up to 0.3)
    # Check for formats like [text], {input}, "input data"
    has_placeholders = bool(re.search(r"\{.*?\}|\[.*?\]|<.*?>", prompt))
    if has_placeholders:
        score += 0.2
    
    # Check for quotes wrapping possible input data
    has_quotes = len(re.findall(r'"[^"]+"|\'[^\']+\'', prompt)) >= 1
    if has_quotes:
        score += 0.1

    # Length reward (up to 0.1) if context statements are typically longer
    word_count = len(clean_prompt.split())
    if word_count > 25:
        score += 0.1

    return min(round(score, 2), 1.0)

def calculate_specificity(prompt: str) -> float:
    """
    Evaluates depth specifications, domain boundaries, and concrete requirements.
    """
    clean_prompt = prompt.strip().lower()
    if not clean_prompt:
        return 0.0

    score = 0.0

    # 1. Depth descriptors (up to 0.3)
    if any(keyword in clean_prompt for keyword in DEPTH_KEYWORDS):
        score += 0.3

    # 2. Target audience qualifiers (up to 0.2)
    if any(re.search(pattern, clean_prompt) for pattern in AUDIENCE_KEYWORDS):
        score += 0.2

    # 3. Boundary / focus markers (up to 0.3)
    boundary_markers = ["specifically", "focus on", "exclude", "only", "boundaries", "scope", "except"]
    if any(marker in clean_prompt for marker in boundary_markers):
        score += 0.3

    # 4. Numerical descriptors/counts (up to 0.2)
    # Looking for digits or numbers that restrict parameters
    has_numbers = bool(re.search(r"\b\d+\b", clean_prompt))
    if has_numbers:
        score += 0.2

    return min(round(score, 2), 1.0)

def calculate_intent(prompt: str) -> float:
    """
    Measures if the request or directive goal is identifiable.
    """
    clean_prompt = prompt.strip().lower()
    if not clean_prompt:
        return 0.0

    score = 0.0

    # 1. Start of prompt has action verb or question word (up to 0.5)
    sentences = re.split(r"[.!?]+", clean_prompt)
    if sentences:
        first_sentence = sentences[0].strip()
        words = first_sentence.split()
        if words:
            first_word = words[0]
            # Action verbs
            if first_word in ACTION_VERBS:
                score += 0.5
            # Question words indicating intent
            elif first_word in ["what", "how", "why", "who", "which", "where", "can", "could", "write"]:
                score += 0.4

    # 2. Action patterns within prompt (up to 0.3)
    intent_phrases = ["your task is", "please do", "i want you to", "your goal is", "i need to", "help me to"]
    if any(phrase in clean_prompt for phrase in intent_phrases):
        score += 0.3
    
    # 3. General action verb elsewhere in the prompt (up to 0.2)
    if any(verb in clean_prompt for verb in ACTION_VERBS):
        score += 0.2

    # Fallback default for any non-empty text
    if score == 0.0 and len(clean_prompt) > 0:
        score = 0.2

    return min(round(score, 2), 1.0)

def calculate_constraints(prompt: str) -> float:
    """
    Checks for the presence of explicit guidelines, limits, or negative constraints.
    """
    clean_prompt = prompt.strip().lower()
    if not clean_prompt:
        return 0.0

    score = 0.0

    # 1. Negative directives (up to 0.4)
    if any(re.search(pattern, clean_prompt) for pattern in NEGATIVE_CONSTRAINTS):
        score += 0.4

    # 2. Explicit length/structural limits (up to 0.4)
    if any(keyword in clean_prompt for keyword in LIMIT_KEYWORDS):
        score += 0.4

    # 3. Conditional words indicating logic constraints (up to 0.2)
    conditionals = ["if", "unless", "must", "should", "required", "strict"]
    if any(word in clean_prompt for word in conditionals):
        score += 0.2

    return min(round(score, 2), 1.0)

def calculate_output_format(prompt: str) -> float:
    """
    Checks if formatting commands (e.g. JSON, Table, bullet points) are present.
    """
    clean_prompt = prompt.strip().lower()
    if not clean_prompt:
        return 0.0

    score = 0.0

    # 1. Formatting keywords (up to 0.6)
    if any(keyword in clean_prompt for keyword in FORMAT_KEYWORDS):
        score += 0.6

    # 2. Explicit structural design phrases (up to 0.4)
    format_phrases = [
        "format as", "in a table", "as a list", "bulleted", "numbered", 
        "output format", "response structure", "json object", "code block",
        "structured like", "csv format"
    ]
    if any(phrase in clean_prompt for phrase in format_phrases):
        score += 0.4

    return min(round(score, 2), 1.0)

def calculate_examples(prompt: str) -> float:
    """
    Detects few-shot examples or input-output demonstration templates.
    """
    clean_prompt = prompt.strip().lower()
    if not clean_prompt:
        return 0.0

    score = 0.0

    # 1. Example keyword matches (up to 0.5)
    if any(re.search(pattern, clean_prompt) for pattern in EXAMPLE_KEYWORDS):
        score += 0.5

    # 2. Structural pattern detections (up to 0.5)
    # Check for multi-line inputs with structured separation like Q: / A:, Input: / Output:, etc.
    structural_patterns = [
        r"input\s*:.*?\n.*?output\s*:",
        r"q\s*:.*?\n.*?a\s*:",
        r"example\s*\d+\s*:",
        r"\n-\s*.*?\n-\s*.*?" # multiple dash indicators showing structured points
    ]
    if any(re.search(pattern, clean_prompt, re.IGNORECASE | re.DOTALL) for pattern in structural_patterns):
        score += 0.5

    return min(round(score, 2), 1.0)
