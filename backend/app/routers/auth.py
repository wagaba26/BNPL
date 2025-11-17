from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.models.user import User, UserRole
from app.models.credit_profile import CreditProfile
from app.models.retailer import Retailer
from app.models.lender import Lender
from app.schemas.auth import UserRegister, UserLogin, Token, UserMe

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user. Supports CUSTOMER, RETAILER, and LENDER roles.
    
    LENDER role requires admin_code for due diligence verification.
    """
    try:
        # Determine role (default to CUSTOMER if not specified)
        requested_role = user_data.role or UserRole.CUSTOMER
        print(f"[REGISTER] Received role: {user_data.role}, Using role: {requested_role}")
        
        # Validate admin code for LENDER role
        if requested_role == UserRole.LENDER:
            if not user_data.admin_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Admin code is required for lender registration. Please contact support for due diligence verification.",
                )
            if user_data.admin_code != settings.LENDER_ADMIN_CODE:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid admin code. Lender registration requires proper authorization.",
                )
        
        # Validate trading license for RETAILER role
        if requested_role == UserRole.RETAILER:
            if not user_data.trading_license:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Trading license is required for retailer registration. Please provide your valid trading license number for due diligence verification.",
                )
        
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        # Check if username is provided and if it already exists
        if user_data.username:
            existing_username = db.query(User).filter(User.username == user_data.username).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )

        # Create new user with specified role
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            username=user_data.username,
            phone=user_data.phone,
            password_hash=hashed_password,
            role=requested_role,
        )
        db.add(db_user)
        db.flush()

        # Create role-specific profiles
        if requested_role == UserRole.CUSTOMER:
            # Create default credit profile for customers
            credit_profile = CreditProfile(
                user_id=db_user.id,
                score=300,
                tier="TIER_1",
                max_bnpl_limit=200000.00,
            )
            db.add(credit_profile)
            print(f"[REGISTER] Created CreditProfile for CUSTOMER: {db_user.email}")
        elif requested_role == UserRole.RETAILER:
            # Create retailer profile
            retailer = Retailer(
                user_id=db_user.id,
                business_name=user_data.name,  # Use name as business name initially
                contact_person=user_data.name,
                trading_license=user_data.trading_license,
            )
            db.add(retailer)
            print(f"[REGISTER] Created Retailer profile for RETAILER: {db_user.email} with trading license: {user_data.trading_license}")
        elif requested_role == UserRole.LENDER:
            # Create lender profile
            lender = Lender(
                user_id=db_user.id,
                institution_name=user_data.name,  # Use name as institution name initially
                base_interest_rate=10.00,  # Default interest rate
            )
            db.add(lender)
            print(f"[REGISTER] Created Lender profile for LENDER: {db_user.email}")
        
        db.commit()
        db.refresh(db_user)
        print(f"[REGISTER] User created successfully: {db_user.email}, Role: {db_user.role}")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[REGISTER ERROR] {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.id, "email": db_user.email},
        expires_delta=access_token_expires,
    )

    user_response = UserMe(
        id=db_user.id,
        name=db_user.name,
        username=db_user.username,
        email=db_user.email,
        role=db_user.role,
    )
    print(f"[REGISTER] Returning user with role: {user_response.role}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response,
    }


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token. Accepts either email or username."""
    try:
        print(f"[LOGIN] Attempting login for: {user_data.email_or_username}")
        
        # Try to find user by email or username
        user = None
        
        # Check if input contains @ to determine if it's likely an email
        if "@" in user_data.email_or_username:
            # It's likely an email - try email first
            user = db.query(User).filter(User.email == user_data.email_or_username).first()
            print(f"[LOGIN] Searched by email: {user_data.email_or_username}, found: {user is not None}")
        else:
            # No @ symbol - try username first, then email as fallback
            user = db.query(User).filter(User.username == user_data.email_or_username).first()
            print(f"[LOGIN] Searched by username: {user_data.email_or_username}, found: {user is not None}")
            # If not found by username, try email (in case user entered email without @)
            if not user:
                user = db.query(User).filter(User.email == user_data.email_or_username).first()
                print(f"[LOGIN] Fallback search by email: {user_data.email_or_username}, found: {user is not None}")
        
        if not user:
            print(f"[LOGIN] User not found: {user_data.email_or_username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(user_data.password, user.password_hash):
            print(f"[LOGIN] Password verification failed for user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            print(f"[LOGIN] User is inactive: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

        print(f"[LOGIN] Login successful for user: {user.email}, role: {user.role}")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserMe(
                id=user.id,
                name=user.name,
                username=user.username,
                email=user.email,
                role=user.role,
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[LOGIN ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserMe)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info."""
    return UserMe(
        id=current_user.id,
        name=current_user.name,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
    )

