from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.models.user import User, UserRole
from app.models.credit_profile import CreditProfile
from app.schemas.auth import UserRegister, UserLogin, Token, UserMe

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user (defaults to CUSTOMER role)."""
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

    # Create new user with CUSTOMER role
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        username=user_data.username,
        phone=user_data.phone,
        password_hash=hashed_password,
        role=UserRole.CUSTOMER,
    )
    db.add(db_user)
    db.flush()

    # Create default credit profile
    credit_profile = CreditProfile(
        user_id=db_user.id,
        score=300,
        tier="TIER_1",
        max_bnpl_limit=200000.00,
    )
    db.add(credit_profile)
    db.commit()
    db.refresh(db_user)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.id, "email": db_user.email},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserMe(
            id=db_user.id,
            name=db_user.name,
            username=db_user.username,
            email=db_user.email,
            role=db_user.role,
        ),
    }


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token. Accepts either email or username."""
    # Try to find user by email or username
    user = None
    
    # Check if input contains @ to determine if it's likely an email
    if "@" in user_data.email_or_username:
        # It's likely an email - try email first
        user = db.query(User).filter(User.email == user_data.email_or_username).first()
    else:
        # No @ symbol - try username first, then email as fallback
        user = db.query(User).filter(User.username == user_data.email_or_username).first()
        # If not found by username, try email (in case user entered email without @)
        if not user:
            user = db.query(User).filter(User.email == user_data.email_or_username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

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

