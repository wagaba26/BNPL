from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.models.retailer import Retailer
from app.models.product import Product
from app.models.lender import Lender
from app.models.credit_profile import CreditProfile
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductDetailResponse,
    ProductPrice, ProductBNPL, ProductStock, ProductRetailer
)

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


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get detailed product information for checkout."""
    try:
        product_id_int = int(product_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format",
        )

    # Get product with retailer relationship
    product = db.query(Product).filter(Product.id == product_id_int).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND",
        )

    # Get retailer info
    retailer = db.query(Retailer).filter(Retailer.id == product.retailer_id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer not found",
        )

    # Get lender for BNPL configuration (use first lender or defaults)
    lender = db.query(Lender).first()
    
    # Calculate BNPL details
    # Default: 20% deposit (as per loan creation logic)
    min_deposit_percent = 20.0
    # Default: 3 months tenure (as per loan creation logic - 3 installments)
    max_tenure_months = 3
    # Use lender's interest rate if available, otherwise default to 10%
    interest_rate_percent_per_month = float(lender.base_interest_rate) if lender else 10.0

    # Generate SKU from product ID (fallback if not in DB)
    sku = f"PRD-{product.id:06d}"

    # Format dates
    created_at_str = product.created_at.isoformat() if product.created_at else ""
    updated_at_str = product.updated_at.isoformat() if product.updated_at else created_at_str

    return ProductDetailResponse(
        id=str(product.id),
        name=product.name,
        sku=sku,
        description=product.description or "",
        price=ProductPrice(
            currency="UGX",  # Default currency
            amount=float(product.price)
        ),
        bnpl=ProductBNPL(
            eligible=product.bnpl_eligible,
            min_deposit_percent=min_deposit_percent,
            max_tenure_months=max_tenure_months,
            interest_rate_percent_per_month=interest_rate_percent_per_month
        ),
        stock=ProductStock(
            available_quantity=product.stock,
            is_active=product.stock > 0
        ),
        retailer=ProductRetailer(
            id=str(retailer.id),
            name=retailer.business_name
        ),
        images=[],  # Empty array for now - can be extended later
        created_at=created_at_str,
        updated_at=updated_at_str
    )

