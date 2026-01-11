Write-Host "----------------------------------------------------------------"
Write-Host "   AI Stock Platform Startup (Manual API)"
Write-Host "----------------------------------------------------------------"

# 1. Activate Venv
$venvPath = ".venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating venv..."
    & $venvPath
}

# 2. Check Python
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python not found!"
    exit
}

# 3. Models
if (-not (Test-Path "signals/rf_model.pkl")) {
    Write-Host "Training models..."
    python signals/train_and_save.py
}
else {
    Write-Host "Models found."
}

Write-Host "⚠️  Ensure APIs are running! (Use 'start_services.ps1')"
Write-Host "   - Signals API: Port 8000"
Write-Host "   - Alerts API:  Port 8001"
Write-Host "Starting Dashboard..."
python -m streamlit run 0_Overview.py
