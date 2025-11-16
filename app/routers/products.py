from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import JWTError, jwt
from app.database import get_db
from app.dependencies import get_current_active_user
from app.schemas.product import ProductResponse
from app.models.product import Product
from app.models.user import User
from app.models.credit_profile import CreditProfile
from app.config import settings
from app.services.auth import get_user_by_id

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            return None
        user_id: int = int(user_id_raw)
        user = get_user_by_id(db, user_id=user_id)
        if user and user.is_active:
            return user
    except:
        pass
    return None


@router.get("/", response_model=List[ProductResponse])
async def list_all_products(
    skip: int = 0,
    limit: int = 100,
    bnpl_eligible_only: bool = False,
    refurbished_only: bool = False,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """List all products available for BNPL. Filters by credit score and max_bnpl_limit if user is authenticated."""
    query = db.query(Product).filter(Product.is_active == True)
    
    if bnpl_eligible_only:
        query = query.filter(Product.is_bnpl_eligible == True)
    
    if refurbished_only:
        query = query.filter(Product.is_refurbished == True)
    
    # If user is authenticated, filter by credit profile
    if current_user:
        credit_profile = db.query(CreditProfile).filter(
            CreditProfile.user_id == current_user.id
        ).first()
        
        if credit_profile:
            # Filter by min_required_score
            query = query.filter(
                (Product.min_required_score.is_(None)) | 
                (Product.min_required_score <= credit_profile.score)
            )
            # Filter by max_bnpl_limit
            query = query.filter(Product.price <= credit_profile.max_bnpl_limit)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/refurbished", response_model=List[ProductResponse])
async def list_refurbished_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all refurbished products (from traded-in items)."""
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.is_refurbished == True
    ).offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

