from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_active_user, require_role
from app.schemas.retailer import RetailerCreate, RetailerUpdate, RetailerResponse
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.models.user import User, UserRole
from app.models.retailer import Retailer
from app.models.product import Product

router = APIRouter()


@router.post("/profile", response_model=RetailerResponse, status_code=status.HTTP_201_CREATED)
async def create_retailer_profile(
    retailer_data: RetailerCreate,
    current_user: User = Depends(require_role(UserRole.RETAILER)),
    db: Session = Depends(get_db),
):
    """Create or update retailer profile."""
    # Check if profile already exists
    existing_retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if existing_retailer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Retailer profile already exists",
        )

    retailer_data.user_id = current_user.id
    db_retailer = Retailer(**retailer_data.model_dump())
    db.add(db_retailer)
    db.commit()
    db.refresh(db_retailer)
    return db_retailer


@router.get("/profile", response_model=RetailerResponse)
async def get_retailer_profile(
    current_user: User = Depends(require_role(UserRole.RETAILER)),
    db: Session = Depends(get_db),
):
    """Get retailer profile."""
    retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer profile not found",
        )
    return retailer


@router.put("/profile", response_model=RetailerResponse)
async def update_retailer_profile(
    retailer_update: RetailerUpdate,
    current_user: User = Depends(require_role(UserRole.RETAILER)),
    db: Session = Depends(get_db),
):
    """Update retailer profile."""
    retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer profile not found",
        )

    update_data = retailer_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(retailer, key, value)

    db.commit()
    db.refresh(retailer)
    return retailer


# Product endpoints
@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_role(UserRole.RETAILER)),
    db: Session = Depends(get_db),
):
    """Create a new product."""
    retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer profile not found. Please create your retailer profile first.",
        )

    product_data.retailer_id = retailer.id
    db_product = Product(**product_data.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    current_user: User = Depends(require_role(UserRole.RETAILER)),
    db: Session = Depends(get_db),
):
    """List all products for the current retailer."""
    retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer profile not found",
        )

    products = db.query(Product).filter(Product.retailer_id == retailer.id).all()
    return products


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_user: User = Depends(require_role(UserRole.RETAILER)),
    db: Session = Depends(get_db),
):
    """Get a specific product."""
    retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer profile not found",
        )

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.retailer_id == retailer.id,
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(require_role(UserRole.RETAILER)),
    db: Session = Depends(get_db),
):
    """Update a product."""
    retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer profile not found",
        )

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.retailer_id == retailer.id,
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_role(UserRole.RETAILER)),
    db: Session = Depends(get_db),
):
    """Delete a product."""
    retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer profile not found",
        )

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.retailer_id == retailer.id,
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    db.delete(product)
    db.commit()
    return None

