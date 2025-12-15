@echo off
echo Starting AI Companion Backend...
cd backend
call venv\Scripts\activate.bat
python -m api.main
pause
