# PromptOpt: AI-Driven Prompt Effectiveness Prediction using Bayesian Search and Gradient-Based Prompt Refinement

PromptOpt is an ML engineering tool designed for IEEE publication. It evaluates, scores, and iteratively optimizes LLM prompts using Bayesian search, meta-prompting, and vector caching.

---

## 👥 Team Responsibilities & Project Structure

The project is divided into three major engineering modules:

1. **Member 1: Prompt Analysis & Evaluation (This Module)**
   * Responsible for assessing prompt quality, detecting weaknesses, calculating overall prompt quality scores, and comparing original vs. optimized responses.
   * **Module Path**: [`member1/`](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/)
   * **Documentation**: See [`member1/README.md`](file:///c:/Users/Administrator/Desktop/AI-Prompt-Optimizer/member1/README.md) for full instructions and formulas.
   
2. **Member 2: Prompt Optimization (Upcoming)**
   * Responsible for Bayesian search algorithms and gradient-based prompt refinement loops.
   
3. **Member 3: Integration & UI (Upcoming)**
   * Responsible for FastAPI/Streamlit components, database caching, and hosting LLM API integrations.

---

## 🚀 Getting Started (Member 1 Module)

To set up and run Member 1's Prompt Analysis and Response Evaluation module locally:

1. **Setup the Virtual Environment**:
   ```cmd
   setup_venv.bat
   ```
   *(Creates a `.venv` virtual environment and installs dependencies from `requirements.txt`.)*
   
2. **Activate the Environment**:
   * Command Prompt: `.venv\Scripts\activate.bat`
   * PowerShell: `.venv\Scripts\Activate.ps1`
   
3. **Run Unit Tests**:
   ```bash
   pytest member1/tests/
   ```

4. **Run the Demonstration**:
   ```bash
   python member1/integration_demo.py
   ```
