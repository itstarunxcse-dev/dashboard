Write-Host "Starting Core Services..."

# Start Signals API (Port 8000)
Start-Process python -ArgumentList "signals/api.py" -WindowStyle Minimized
Write-Host "✅ Signals API started on Port 8000"

# Start Alerts API (Port 8001)
Start-Process python -ArgumentList "alerts/main.py" -WindowStyle Minimized
Write-Host "✅ Alerts API started on Port 8001"

Write-Host "Services are running in background windows."
Write-Host "You can now run 'run_project.ps1' to start the dashboard."
