from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import (
    auth,
    users,
    merchants,
    lenders,
    products,
    loans,
    payments,
    scoring,
    webhooks,
    assets,
)
from app.services.collections import collections_service

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize scheduler
scheduler = BackgroundScheduler()


def run_daily_collections_check():
    """Function to run daily collections check."""
    db = SessionLocal()
    try:
        result = collections_service.run_daily_collections_check(db)
        print(f"[SCHEDULER] Daily collections check completed: {result}")
    except Exception as e:
        print(f"[SCHEDULER] Error in daily collections check: {str(e)}")
    finally:
        db.close()


# Schedule daily collections check at 9:00 AM UTC every day
scheduler.add_job(
    run_daily_collections_check,
    trigger=CronTrigger(hour=9, minute=0),  # Run at 9:00 AM UTC daily
    id='daily_collections_check',
    name='Daily Collections and Reminder Check',
    replace_existing=True
)

app = FastAPI(
    title=settings.APP_NAME,
    description="Buy Now Pay Later (BNPL) Fintech Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(merchants.router, prefix="/api/v1/merchants", tags=["Merchants"])
app.include_router(lenders.router, prefix="/api/v1/lenders", tags=["Lenders"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(loans.router, prefix="/api/v1/loans", tags=["Loans"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(scoring.router, prefix="/api/v1/scoring", tags=["Credit Scoring"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets & Trade-ins"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to BNPL Platform API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the application starts."""
    scheduler.start()
    print("[SCHEDULER] Collections scheduler started. Daily check scheduled at 9:00 AM UTC.")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown the scheduler when the application stops."""
    scheduler.shutdown()
    print("[SCHEDULER] Collections scheduler stopped.")

