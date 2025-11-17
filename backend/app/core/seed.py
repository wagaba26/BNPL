"""
Development data seeding module.

This module provides functions to seed the database with default development accounts.
Only runs when DEV_SEED environment variable is set to True.
"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.credit_profile import CreditProfile
from app.models.retailer import Retailer
from app.models.lender import Lender


def seed_dev_accounts(db: Session = None) -> None:
    """
    Seed development accounts for CUSTOMER, RETAILER, and LENDER roles.
    
    This function is idempotent - it will skip creating users that already exist.
    Only runs in development mode when DEV_SEED is enabled.
    
    Args:
        db: Optional database session. If not provided, creates a new session.
    """
    # Create all tables if they don't exist (useful for SQLite development)
    Base.metadata.create_all(bind=engine)
    
    if db is None:
        db = SessionLocal()
        try:
            _seed_dev_accounts_internal(db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    else:
        _seed_dev_accounts_internal(db)


def _seed_dev_accounts_internal(db: Session) -> None:
    """Internal function that performs the actual seeding."""
    
    # 1. CUSTOMER account
    customer_email = "wagabac"
    customer_username = "wagabac"
    customer = db.query(User).filter(User.email == customer_email).first()
    if not customer:
        print(f"[SEED] Creating CUSTOMER account: {customer_email}")
        customer = User(
            name="Dev Customer",
            username=customer_username,
            email=customer_email,
            phone="+256700000001",
            password_hash=get_password_hash("admin"),
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        db.add(customer)
        db.flush()  # Flush to get the user ID
        
        # Create CreditProfile for customer
        credit_profile = CreditProfile(
            user_id=customer.id,
            score=500,
            tier="TIER_2",
            max_bnpl_limit=800000.00,
        )
        db.add(credit_profile)
        print(f"[SEED] Created CreditProfile for {customer_email} (score: 500, tier: TIER_2, limit: 800000)")
    else:
        # Update existing user to ensure it's properly configured
        updated = False
        if not customer.username or customer.username != customer_username:
            customer.username = customer_username
            updated = True
        if not customer.is_active:
            customer.is_active = True
            updated = True
        if customer.role != UserRole.CUSTOMER:
            customer.role = UserRole.CUSTOMER
            updated = True
        # Reset password to ensure it's "admin"
        customer.password_hash = get_password_hash("admin")
        updated = True
        
        if updated:
            db.add(customer)
            print(f"[SEED] Updated CUSTOMER account {customer_email} with username, password, and active status")
        else:
            print(f"[SEED] CUSTOMER account {customer_email} already exists and is properly configured")
        
        # Ensure CreditProfile exists
        credit_profile = db.query(CreditProfile).filter(CreditProfile.user_id == customer.id).first()
        if not credit_profile:
            credit_profile = CreditProfile(
                user_id=customer.id,
                score=500,
                tier="TIER_2",
                max_bnpl_limit=800000.00,
            )
            db.add(credit_profile)
            print(f"[SEED] Created CreditProfile for existing customer {customer_email}")
    
    # 2. RETAILER account
    retailer_email = "wagabar"
    retailer_username = "wagabar"
    retailer_user = db.query(User).filter(User.email == retailer_email).first()
    if not retailer_user:
        print(f"[SEED] Creating RETAILER account: {retailer_email}")
        retailer_user = User(
            name="Dev Retailer",
            username=retailer_username,
            email=retailer_email,
            phone="+256700000002",
            password_hash=get_password_hash("admin"),
            role=UserRole.RETAILER,
            is_active=True,
        )
        db.add(retailer_user)
        db.flush()  # Flush to get the user ID
        
        # Create Retailer profile
        retailer = Retailer(
            user_id=retailer_user.id,
            business_name="Dev Retailer Store",
            payout_account="dev-payout",
        )
        db.add(retailer)
        print(f"[SEED] Created Retailer profile for {retailer_email}")
    else:
        # Update existing user to ensure it's properly configured
        updated = False
        if not retailer_user.username or retailer_user.username != retailer_username:
            retailer_user.username = retailer_username
            updated = True
        if not retailer_user.is_active:
            retailer_user.is_active = True
            updated = True
        if retailer_user.role != UserRole.RETAILER:
            retailer_user.role = UserRole.RETAILER
            updated = True
        # Reset password to ensure it's "admin"
        retailer_user.password_hash = get_password_hash("admin")
        updated = True
        
        if updated:
            db.add(retailer_user)
            print(f"[SEED] Updated RETAILER account {retailer_email} with username, password, and active status")
        else:
            print(f"[SEED] RETAILER account {retailer_email} already exists and is properly configured")
        
        # Ensure Retailer profile exists
        retailer = db.query(Retailer).filter(Retailer.user_id == retailer_user.id).first()
        if not retailer:
            retailer = Retailer(
                user_id=retailer_user.id,
                business_name="Dev Retailer Store",
                payout_account="dev-payout",
            )
            db.add(retailer)
            print(f"[SEED] Created Retailer profile for existing retailer {retailer_email}")
    
    # 3. LENDER account
    lender_email = "wagabal"
    lender_username = "wagabal"
    lender_user = db.query(User).filter(User.email == lender_email).first()
    if not lender_user:
        print(f"[SEED] Creating LENDER account: {lender_email}")
        lender_user = User(
            name="Dev Lender",
            username=lender_username,
            email=lender_email,
            phone="+256700000003",
            password_hash=get_password_hash("admin"),
            role=UserRole.LENDER,
            is_active=True,
        )
        db.add(lender_user)
        db.flush()  # Flush to get the user ID
        
        # Create Lender profile
        lender = Lender(
            user_id=lender_user.id,
            institution_name="Dev Lender MFI",
            base_interest_rate=10.00,
        )
        db.add(lender)
        print(f"[SEED] Created Lender profile for {lender_email}")
    else:
        # Update existing user to ensure it's properly configured
        updated = False
        if not lender_user.username or lender_user.username != lender_username:
            lender_user.username = lender_username
            updated = True
        if not lender_user.is_active:
            lender_user.is_active = True
            updated = True
        if lender_user.role != UserRole.LENDER:
            lender_user.role = UserRole.LENDER
            updated = True
        # Reset password to ensure it's "admin"
        lender_user.password_hash = get_password_hash("admin")
        updated = True
        
        if updated:
            db.add(lender_user)
            print(f"[SEED] Updated LENDER account {lender_email} with username, password, and active status")
        else:
            print(f"[SEED] LENDER account {lender_email} already exists and is properly configured")
        
        # Ensure Lender profile exists
        lender = db.query(Lender).filter(Lender.user_id == lender_user.id).first()
        if not lender:
            lender = Lender(
                user_id=lender_user.id,
                institution_name="Dev Lender MFI",
                base_interest_rate=10.00,
            )
            db.add(lender)
            print(f"[SEED] Created Lender profile for existing lender {lender_email}")
    
    print("[SEED] Development account seeding completed!")

