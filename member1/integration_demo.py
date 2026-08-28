"""
integration_demo.py

Demonstration script showing the full Prompt Analysis, Scorer, Weakness Detection,
and Response Evaluation flow for the PromptOpt (Member 1) module.
Runs 9 different prompts representing different prompt engineering strengths, and
compares an original versus optimized response.
"""

import sys
import os

# Append current directory to path to ensure imports work if run as script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from member1 import (
    analyze_prompt,
    detect_weaknesses,
    calculate_prompt_score,
    evaluate_response
)

# 10 test cases (9 valid, 1 invalid to test exception handling)
test_prompts = [
    # 1. Very weak prompt (No context, format, specificity, constraints, examples)
    "Explain machine learning.",
    
    # 2. Another weak prompt
    "Write python code.",
    
    # 3. Prompt with clarity and intent, but minimal context/format
    "Write a Python function that calculates the Fibonacci sequence up to N.",
    
    # 4. Prompt with constraints
    "Explain quantum computing in under 100 words. Do not use complex math jargon.",
    
    # 5. Prompt with format instruction
    "List the top 5 programming languages in 2026. Format as a markdown table.",
    
    # 6. Prompt with role and context
    "You are a technical recruiter. Write an email to a senior candidate inviting them for a system design interview.",
    
    # 7. Prompt with few-shot examples
    "Translate English slang to formal text. E.g., 'hang out' -> 'spend time together'. Translate: 'that is sick'.",
    
    # 8. Strong prompt (Clarity, context, intent, specificity, constraints, format)
    "You are an experienced python data scientist. Write a python script to load a CSV file named 'data.csv', clean missing values by filling them with the column mean, and output a summary table of the data. Word limit: 100 lines. Do not use external libraries other than pandas and numpy. Format output as raw code blocks.",
    
    # 9. Extremely strong prompt (Clarity, context, intent, specificity, constraints, format, and examples)
    "You are a database optimizer. Check the following query for performance issues and provide suggestions.\n"
    "Query: SELECT * FROM users JOIN orders ON users.id = orders.user_id WHERE users.signup_date > '2026-01-01';\n"
    "Example query optimization:\n"
    "Original: SELECT * FROM logs WHERE log_level = 'ERROR';\n"
    "Optimized: CREATE INDEX idx_log_level ON logs(log_level); SELECT id, timestamp, message FROM logs WHERE log_level = 'ERROR';\n"
    "Format the response in three sections: 1. Identified Issues, 2. Optimized SQL, 3. Explanation.\n"
    "Constraints: Keep explanations under 200 words. Do not suggest hardware upgrades.",
    
    # 10. Invalid prompt (empty) to demonstrate input validation
    ""
]

def run_demo():
    print("=" * 80)
    print("PROMPTOPT: PROMPT ANALYSIS & EVALUATION MODULE (MEMBER 1) DEMO")
    print("=" * 80)
    
    # Run analysis, scorer, and weakness detection on prompts 1-9
    for idx, prompt in enumerate(test_prompts[:-1], 1):
        print(f"\n--- TEST PROMPT #{idx} ---")
        print(f"Prompt text:\n{prompt}\n")
        
        try:
            # Step A: Analyze Prompt Heuristics
            analysis = analyze_prompt(prompt)
            
            # Step B: Score Prompt Quality
            score_data = calculate_prompt_score(analysis)
            
            # Step C: Detect Weaknesses
            weaknesses = detect_weaknesses(analysis)
            
            # Display results
            print("Metric Scores:")
            for metric, score in analysis["metrics"].items():
                print(f"  - {metric.replace('_', ' ').capitalize()}: {score:.2f}")
                
            print(f"Overall Quality Score: {score_data['score']}/100")
            print(f"Grade: {score_data['grade']}")
            
            if weaknesses:
                print("Detected Weaknesses:")
                for weakness in weaknesses:
                    print(f"  [!] {weakness}")
            else:
                print("  [✓] No significant weaknesses detected! Prompt is strong.")
                
        except Exception as e:
            print(f"An unexpected error occurred during analysis: {e}")
            
    # Test case 10: Invalid prompt error handling
    print("\n--- TEST PROMPT #10 (Error Handling) ---")
    print("Prompt text: <Empty String>")
    try:
        analyze_prompt(test_prompts[-1])
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {e}")
        
    print("\n" + "=" * 80)
    print("RESPONSE EVALUATION DEMO")
    print("=" * 80)
    
    # Simulate Original vs Optimized Response comparison
    original_resp = (
        "Machine learning is where computers learn from data. It includes supervised, "
        "unsupervised and reinforcement learning."
    )
    
    optimized_resp = (
        "### Machine Learning Overview\n\n"
        "Machine learning (ML) is a subset of artificial intelligence focused on building "
        "systems that learn from, and make decisions based on, data.\n\n"
        "#### Key Types of ML:\n"
        "1. **Supervised Learning**: The model learns from labeled training data (e.g., linear regression, classification).\n"
        "2. **Unsupervised Learning**: The model identifies hidden patterns in unlabeled data (e.g., K-Means clustering).\n"
        "3. **Reinforcement Learning**: An agent learns to make decisions by taking actions in an environment to maximize cumulative reward.\n\n"
        "*Helpful Tip: When selecting an algorithm, always evaluate the dimensionality of your data first.*"
    )
    
    print(f"Original Response (from original prompt):\n{original_resp}\n")
    print(f"Optimized Response (from optimized prompt):\n{optimized_resp}\n")
    
    try:
        # Step D: Evaluate Response Improvement
        # Note: sentence-transformers model will load lazily during this call
        eval_report = evaluate_response(original_resp, optimized_resp)
        
        print("Evaluation Metrics:")
        for metric, score in eval_report["metrics"].items():
            print(f"  - {metric.replace('_', ' ').capitalize()}: {score:.2f}")
            
        print(f"Optimized Response Overall Score: {eval_report['overall_score']}/100")
        print(f"Improvement: {eval_report['improvement']}%")
        print(f"Better Response Decision: {eval_report['better_response'].upper()}")
        
    except Exception as e:
        print(f"An error occurred during response evaluation: {e}")
        
    print("\n" + "=" * 80)
    print("DEMO RUN COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    run_demo()
