# =====================================================================
# The Useless Oracle - Environment Setup Script (Windows 11)
# =====================================================================
# Usage (run from the project root, in PowerShell):
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\setup.ps1
# =====================================================================

Write-Host "=== The Useless Oracle: Environment Setup ===" -ForegroundColor Cyan

# --- Step 1: Check Python ---
Write-Host "`n[1/7] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found on PATH." -ForegroundColor Red
    Write-Host "Install Python 3.10+ from https://www.python.org/downloads/ (check 'Add to PATH' during install), then re-run this script." -ForegroundColor Red
    exit 1
}
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# --- Step 2: Create virtual environment ---
Write-Host "`n[2/7] Creating virtual environment (.venv)..." -ForegroundColor Yellow
if (-Not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists, skipping." -ForegroundColor Green
}

# --- Step 3: Activate venv & install dependencies ---
Write-Host "`n[3/7] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"
pip install --upgrade pip | Out-Null
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed. Check requirements.txt and your internet connection." -ForegroundColor Red
    exit 1
}
Write-Host "Dependencies installed." -ForegroundColor Green

# --- Step 4: Verify NVIDIA GPU + driver are visible ---
Write-Host "`n[4/7] Verifying NVIDIA GPU..." -ForegroundColor Yellow
$nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($nvidiaSmi) {
    Write-Host "GPU detected:" -ForegroundColor Green
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
} else {
    Write-Host "WARNING: nvidia-smi not found." -ForegroundColor Red
    Write-Host "Ollama will silently fall back to CPU inference, which will be much slower on stage." -ForegroundColor Red
    Write-Host "Install/update drivers from https://www.nvidia.com/Download/index.aspx" -ForegroundColor Red
}

# --- Step 5: Check Ollama is installed ---
Write-Host "`n[5/7] Checking Ollama installation..." -ForegroundColor Yellow
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
if (-Not $ollamaCmd) {
    Write-Host "ERROR: Ollama not found in PATH." -ForegroundColor Red
    Write-Host "Download and install it from https://ollama.com/download/windows, then re-run this script." -ForegroundColor Red
    exit 1
}
Write-Host "Ollama found at: $($ollamaCmd.Source)" -ForegroundColor Green

# --- Step 6: Check the Ollama background service, start it if needed ---
Write-Host "`n[6/7] Checking Ollama service on localhost:11434..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://localhost:11434" -UseBasicParsing -TimeoutSec 3 | Out-Null
    Write-Host "Ollama service is already running." -ForegroundColor Green
} catch {
    Write-Host "Service not responding - starting it in the background..." -ForegroundColor Yellow
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "Ollama service started." -ForegroundColor Green
}

# --- Step 7: Pull the model(s) we'll use ---
Write-Host "`n[7/7] Pulling local models (first pull can take a few minutes)..." -ForegroundColor Yellow
Write-Host "Pulling llama3.2:3b  (~2.0 GB, fastest - good default for live demos)..." -ForegroundColor Cyan
ollama pull llama3.2:3b

Write-Host "Pulling qwen2.5:7b   (~4.7 GB, slower but more dramatic/coherent personas)..." -ForegroundColor Cyan
ollama pull qwen2.5:7b

Write-Host "`n=== Setup complete! ===" -ForegroundColor Cyan
Write-Host "Your 8GB RTX 5060 has headroom for either model fully offloaded to VRAM."
Write-Host "Next time, just activate the environment with:"
Write-Host "    .venv\Scripts\Activate.ps1"
Write-Host "We'll build main.py and ollama_client.py in Step 2."
