@echo off
echo Creating Python virtual environment in .venv...
python -m venv .venv

if %errorlevel% neq 0 (
    echo Failed to create virtual environment. Make sure Python is installed and in your PATH.
    exit /b %errorlevel%
)

echo Activating virtual environment and installing dependencies...
call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Dependency installation failed.
    exit /b %errorlevel%
)

echo Virtual environment setup successfully!
echo To activate it in your terminal, run: .venv\Scripts\activate.bat
