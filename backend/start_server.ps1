Write-Host "Starting BNPL Backend Server..." -ForegroundColor Green
Write-Host ""
$env:DATABASE_URL = "sqlite:///./bnpl_dev.db"
$env:DEV_SEED = "true"
uvicorn app.main:app --reload --port 8000

