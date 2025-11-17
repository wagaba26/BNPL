@echo off
echo Starting BNPL Backend Server...
echo.
set DATABASE_URL=sqlite:///./bnpl_dev.db
set DEV_SEED=true
uvicorn app.main:app --reload --port 8000

