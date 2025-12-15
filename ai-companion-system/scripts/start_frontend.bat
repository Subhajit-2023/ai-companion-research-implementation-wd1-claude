@echo off
echo Starting AI Companion System Frontend...
echo.

cd /d "%~dp0..\frontend"

if not exist "node_modules" (
    echo Node modules not found!
    echo Running npm install...
    call npm install
)

echo Starting Vite dev server...
call npm run dev

pause
