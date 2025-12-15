# AI Companion System - Windows Setup Script
# Run as Administrator

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "AI Companion System - Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or 3.11 from python.org" -ForegroundColor Red
    exit 1
}
$pythonVersion = python --version
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "ERROR: Node.js not found!" -ForegroundColor Red
    Write-Host "Please install Node.js 18+ from nodejs.org" -ForegroundColor Red
    exit 1
}
$nodeVersion = node --version
Write-Host "Found: Node.js $nodeVersion" -ForegroundColor Green

# Check NVIDIA GPU
Write-Host "Checking NVIDIA GPU..." -ForegroundColor Yellow
$nvidia = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($nvidia) {
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    Write-Host "GPU detected!" -ForegroundColor Green
} else {
    Write-Host "WARNING: nvidia-smi not found. GPU may not be available." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setting up backend..." -ForegroundColor Cyan

# Create virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
Set-Location backend
python -m venv venv
Write-Host "Virtual environment created!" -ForegroundColor Green

# Activate virtual environment and install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Backend dependencies installed!" -ForegroundColor Green

Set-Location ..

Write-Host ""
Write-Host "Setting up frontend..." -ForegroundColor Cyan
Set-Location frontend
npm install
Write-Host "Frontend dependencies installed!" -ForegroundColor Green

Set-Location ..

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Install Ollama from https://ollama.ai/download" -ForegroundColor White
Write-Host "2. Run: ollama pull dolphin-mistral:7b-v2.8" -ForegroundColor White
Write-Host "3. Download and setup Stable Diffusion WebUI" -ForegroundColor White
Write-Host "4. Configure models (see docs/MODELS_SETUP.md)" -ForegroundColor White
Write-Host ""
Write-Host "To start the system:" -ForegroundColor Yellow
Write-Host "  Backend:  cd backend && .\venv\Scripts\Activate.ps1 && python -m api.main" -ForegroundColor White
Write-Host "  Frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
