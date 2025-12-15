@echo off
echo Starting AI Companion System Backend...
echo.

cd /d "%~dp0..\backend"

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Starting FastAPI server...
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

pause
