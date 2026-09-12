# =====================================================================
# The Useless Oracle — Build script: packages main.py into a standalone
# Windows .exe using PyInstaller.
#
# Run from the project root, with the venv already set up:
#   .\build_exe.ps1
#
# NOTE: this bundles YOUR app, not Ollama. Ollama must still be installed
# and running (ollama serve) on whatever machine actually runs the .exe,
# with the model already pulled — same as running python main.py directly.
# =====================================================================

Write-Host "=== The Useless Oracle: Build .exe ===" -ForegroundColor Cyan

# --- Step 1: Activate the venv ---
Write-Host "`n[1/3] Activating virtual environment..." -ForegroundColor Yellow
if (-Not (Test-Path ".venv")) {
    Write-Host "ERROR: .venv not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}
& ".venv\Scripts\Activate.ps1"

# --- Step 2: Make sure PyInstaller is installed ---
Write-Host "`n[2/3] Checking PyInstaller..." -ForegroundColor Yellow
pip show pyinstaller > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller not found, installing from requirements.txt..." -ForegroundColor Yellow
    pip install pyinstaller==6.11.1
}
Write-Host "PyInstaller ready." -ForegroundColor Green

# --- Step 3: Build ---
# --onefile        : produces a single .exe instead of a folder of files (easier to hand to judges)
# --windowed       : suppresses the black console window behind the GUI
# --name           : sets the output filename
# --collect-all    : CustomTkinter and pynvml ship non-Python data/asset files
#                    (themes, icons) that PyInstaller's import analysis alone
#                    won't find — this forces it to grab everything from
#                    these packages, not just the .py source.
# config.py, theme.py, ollama_client.py, telemetry.py, gauge.py are picked
# up automatically since main.py imports them directly and they sit next
# to it — no extra flags needed for our own modules.
Write-Host "`n[3/3] Building UselessOracle.exe (this can take a minute or two)..." -ForegroundColor Yellow
pyinstaller --noconfirm --onefile --windowed --name "UselessOracle" `
    --collect-all customtkinter `
    --collect-all pynvml `
    main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller build failed. Scroll up for the actual error." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Build complete! ===" -ForegroundColor Cyan
Write-Host "Your .exe is at: dist\UselessOracle.exe"
Write-Host "Before demoing on another machine: Ollama must be installed there too,"
Write-Host "with 'ollama serve' running and your model already pulled."
