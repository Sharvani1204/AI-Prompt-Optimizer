# Implementation Plan - Prompt Analysis & Evaluation (Member 1)

This plan outlines the architecture, data structures, heuristics, and verification strategy for the **Prompt Analysis & Evaluation** module of the **PromptOpt** project.

## Goal Description
Build a production-quality, independently testable, and explainable module that assesses LLM prompts (for clarity, context, specificity, intent, constraints, format, and examples) and evaluates response improvements (using local semantic similarity embeddings and providing a clean interface for future LLM-as-a-Judge evaluations).

---

## Proposed Changes

We will create a self-contained module under the directory `member1/` and setup files at the root level of the workspace: `c:\Users\Administrator\Desktop\AI-Prompt-Optimizer`.

```
member1/
│
├── __init__.py
├── metrics.py              # Heuristics for the 7 prompt metrics
├── prompt_analyzer.py      # Core analyzer (returns metric dictionary)
├── weakness_detector.py    # Detects weaknesses based on configured thresholds
├── prompt_scorer.py        # Weighted scorer (returns final grade, weights, 0-100 score)
├── response_evaluator.py   # Response comparator (semantic similarity, mock judge, metrics)
│
├── tests/                  # Unit tests for all modules
│   ├── __init__.py
│   ├── test_prompt_analyzer.py
│   ├── test_weakness_detector.py
│   ├── test_prompt_scorer.py
│   └── test_response_evaluator.py
│
├── README.md               # User documentation for the module
│
└── integration_demo.py     # Clean integration demo showcasing the complete flow
│
requirements.txt            # Dependency list
.gitignore                  # Append python-specific ignores (already present, verify venv is ignored)
```

### 1. Root Configurations & Dependencies

#### [NEW] [requirements.txt](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/requirements.txt)
We will create this file to specify required packages:
* `numpy` (numerical ops)
* `scikit-learn` (for cosine similarity calculation)
* `sentence-transformers` (lightweight embeddings model)
* `pytest` (unit tests framework)

### 2. Module Implementations

#### [NEW] [__init__.py](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/__init__.py)
* Expose the core public functions:
  * `analyze_prompt(prompt: str) -> dict`
  * `detect_weaknesses(analysis: dict) -> list[str]`
  * `calculate_prompt_score(analysis: dict) -> dict`
  * `evaluate_response(original_response: str, optimized_response: str) -> dict`

#### [NEW] [metrics.py](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/metrics.py)
This module contains the logic and helpers to score a prompt against the 7 mandatory metrics:
1. **Clarity**: Heuristics to check word count limits, vocabulary complexity/ambiguity indicators, and grammatical indicators (e.g., active verbs, command verbs).
2. **Context**: Detection of role statements ("act as", "you are a"), input brackets (`[]`, `{{}}`), or descriptive domain context.
3. **Specificity**: Length penalty/rewards, specific details (numbers, measurements), depth terms ("comprehensive", "in-depth").
4. **Intent**: Checks for command/imperative verbs ("summarize", "extract", "write") at the start or inside sentences.
5. **Constraints**: Look for length bounds ("under 100 words", "max 3 paragraphs") and negative directives ("do not", "avoid").
6. **Output Format**: Look for formatting keywords ("JSON", "CSV", "markdown table", "bullet list").
7. **Examples**: Look for demonstration cues ("for example", "e.g.", "sample:", "Input:/Output:").

#### [NEW] [prompt_analyzer.py](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/prompt_analyzer.py)
* Entry point for analyzing a prompt.
* Validates inputs (non-empty string, types, lengths).
* Invokes functions in `metrics.py` and builds a structured, JSON-serializable output.

#### [NEW] [weakness_detector.py](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/weakness_detector.py)
* Inspects the output of `analyze_prompt`.
* Uses a configurable threshold (e.g. `LOW_SCORE_THRESHOLD = 0.40`).
* Generates actionable text recommendations for each metric that falls below the threshold.

#### [NEW] [prompt_scorer.py](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/prompt_scorer.py)
* Computes the weighted prompt quality score ($Q_p = \sum w_i s_i$).
* Default weights sum to $1.0$:
  * Clarity: `0.20`, Context: `0.15`, Specificity: `0.20`, Intent: `0.15`, Constraints: `0.10`, Format: `0.10`, Examples: `0.10`.
* Assigns letter grades based on configured scale:
  * $90\text{-}100$: Excellent, $75\text{-}89$: Good, $60\text{-}74$: Fair, $40\text{-}59$: Weak, $0\text{-}39$: Poor.
* Returns a structured dictionary containing `score`, `score_100`, `grade`, and the `weights` map.

#### [NEW] [response_evaluator.py](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/response_evaluator.py)
* Evaluates original vs optimized responses.
* Uses `sentence-transformers/all-MiniLM-L6-v2` for semantic embeddings, lazily loading the model to prevent startup lags.
* Calculates **Semantic Similarity** via cosine similarity (normalized to `[0.0, 1.0]`).
* Standardizes placeholder scores for subjective axes (Relevance, Accuracy, Completeness, Coherence, Helpfulness) with clear instructions for future integration of LLM-as-a-Judge API or rule-based evaluators.
* Computes overall weighted response score and returns `better_response` ("original", "optimized", or "similar").

#### [NEW] [integration_demo.py](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/integration_demo.py)
* A script containing at least 10 different prompt test cases (both weak and strong prompts).
* Simulates the optimization process (using mock optimization) and evaluates responses.

---

## Verification Plan

### Automated Tests (pytest)
We will run `pytest` to execute all unit tests.

#### [NEW] [test_prompt_analyzer.py](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/tests/test_prompt_analyzer.py)
* Tests response to valid and invalid inputs.
* Verifies structure of returned dict.

#### [NEW] [test_weakness_detector.py](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/tests/test_weakness_detector.py)
* Tests that weakness reports are triggered correctly when scores fall below thresholds.

#### [NEW] [test_prompt_scorer.py](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/tests/test_prompt_scorer.py)
* Verifies weights sum to 1.
* Validates score calculations and grading scale.

#### [NEW] [test_response_evaluator.py](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/tests/test_response_evaluator.py)
* Tests semantic similarity calculations.
* Verifies that identical responses return `1.0` semantic similarity and "similar" comparison result.
* Validates inputs (empty strings, `None` values, etc.).

### Manual Verification
1. Setup local Python virtual environment `.venv`.
2. Install dependencies via `pip install -r requirements.txt`.
3. Run `pytest` to verify 100% test passing rate.
4. Execute `python member1/integration_demo.py` and inspect output logging.
