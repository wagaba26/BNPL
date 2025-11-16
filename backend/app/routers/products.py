from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.models.retailer import Retailer
from app.models.product import Product
from app.models.credit_profile import CreditProfile
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()


@router.get("", response_model=List[ProductResponse])
async def get_products(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get products available for BNPL (CUSTOMER only, filtered by credit profile)."""
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can view products",
        )

    # Get customer's credit profile
    credit_profile = db.query(CreditProfile).filter(
        CreditProfile.user_id == current_user.id
    ).first()

    if not credit_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit profile not found",
        )

    # Filter products based on eligibility
    query = db.query(Product).filter(
        Product.bnpl_eligible == True,
        Product.stock > 0,
    )

    # Filter by min_required_score if set
    if credit_profile.score is not None:
        query = query.filter(
            (Product.min_required_score.is_(None)) |
            (Product.min_required_score <= credit_profile.score)
        )

    # Filter by max_bnpl_limit
    query = query.filter(Product.price <= credit_profile.max_bnpl_limit)

    products = query.all()
    return products


@router.get("/retailer/products", response_model=List[ProductResponse])
async def get_retailer_products(
    current_user: User = Depends(require_role([UserRole.RETAILER])),
    db: Session = Depends(get_db),
):
    """List retailer's own products."""
    retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer profile not found",
        )

    products = db.query(Product).filter(Product.retailer_id == retailer.id).all()
    return products


@router.post("/retailer/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_role([UserRole.RETAILER])),
    db: Session = Depends(get_db),
):
    """Create a new product."""
    retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer profile not found",
        )

    db_product = Product(
        retailer_id=retailer.id,
        **product_data.model_dump(),
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/retailer/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_role([UserRole.RETAILER])),
    db: Session = Depends(get_db),
):
    """Update a product."""
    retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer profile not found",
        )

    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.retailer_id == retailer.id,
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/retailer/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_role([UserRole.RETAILER])),
    db: Session = Depends(get_db),
):
    """Delete a product."""
    retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer profile not found",
        )

    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.retailer_id == retailer.id,
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    db.delete(db_product)
    db.commit()
    return None

