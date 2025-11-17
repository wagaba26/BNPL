from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.core.seed import seed_dev_accounts
from app.routers import auth, credit_profile, products, loans, credit, lender, retailer

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Buy Now Pay Later (BNPL) Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
cors_origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(credit_profile.router, prefix="/credit-profile", tags=["Credit Profile"])
app.include_router(credit.router, prefix="/credit", tags=["Credit Scoring"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(loans.router, prefix="/loans", tags=["Loans"])
app.include_router(lender.router, prefix="/lender", tags=["Lender"])
app.include_router(retailer.router, prefix="/retailer", tags=["Retailer"])


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
    """Seed development accounts if DEV_SEED is enabled."""
    if settings.DEV_SEED:
        print("[STARTUP] DEV_SEED is enabled, seeding development accounts...")
        try:
            seed_dev_accounts()
            print("[STARTUP] Development accounts seeded successfully!")
        except Exception as e:
            print(f"[STARTUP] Error seeding development accounts: {e}")
            # Don't raise - allow app to start even if seeding fails
    else:
        print("[STARTUP] DEV_SEED is disabled, skipping development account seeding")

