from datetime import datetime, timedelta
from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.models.retailer import Retailer
from app.models.product import Product
from app.models.loan import Loan
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from pydantic import BaseModel


router = APIRouter()


class BestSellingProduct(BaseModel):
    product_id: str
    name: str
    sku: str
    bnpl_sales_count: int
    bnpl_sales_amount: float


class RetailerStats(BaseModel):
    retailer_id: str
    currency: str
    total_bnpl_sales: float
    bnpl_transactions_30d: int
    avg_ticket_size_30d: float
    conversion_rate_30d: float  # 0-1
    best_selling_products: List[BestSellingProduct]
    updated_at: str


@router.get("/stats", response_model=RetailerStats)
async def get_retailer_stats(
    current_user: User = Depends(require_role([UserRole.RETAILER])),
    db: Session = Depends(get_db),
):
    """Get retailer dashboard statistics."""
    try:
        # Get retailer profile
        retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
        if not retailer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Retailer profile not found",
            )

        # Get all products for this retailer
        products = db.query(Product).filter(Product.retailer_id == retailer.id).all()
        product_ids = [p.id for p in products]

        if not product_ids:
            # No products, return empty stats
            return RetailerStats(
                retailer_id=str(retailer.id),
                currency="UGX",
                total_bnpl_sales=0.0,
                bnpl_transactions_30d=0,
                avg_ticket_size_30d=0.0,
                conversion_rate_30d=0.0,
                best_selling_products=[],
                updated_at=datetime.utcnow().isoformat()
            )

        # Get all loans for products from this retailer
        all_loans = db.query(Loan).filter(Loan.product_id.in_(product_ids)).all()

        # Calculate total BNPL sales (sum of all loan amounts)
        total_bnpl_sales = sum(float(loan.total_amount) for loan in all_loans)

        # Calculate 30-day stats
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        loans_30d = [
            loan for loan in all_loans
            if loan.created_at and loan.created_at >= thirty_days_ago
        ]

        bnpl_transactions_30d = len(loans_30d)
        
        # Calculate average ticket size for last 30 days
        if loans_30d:
            total_sales_30d = sum(float(loan.total_amount) for loan in loans_30d)
            avg_ticket_size_30d = total_sales_30d / bnpl_transactions_30d
        else:
            avg_ticket_size_30d = 0.0

        # Calculate conversion rate (loans / total products views would require tracking)
        # For now, use a simple metric: loans / total products
        # This is a placeholder - in production you'd track actual product views
        conversion_rate_30d = 0.0  # Default to 0, can be enhanced with view tracking

        # Get best selling products (top 5 by sales amount)
        product_sales = {}
        for loan in all_loans:
            product_id = loan.product_id
            if product_id not in product_sales:
                product_sales[product_id] = {
                    'count': 0,
                    'amount': Decimal('0')
                }
            product_sales[product_id]['count'] += 1
            product_sales[product_id]['amount'] += loan.total_amount

        # Sort by sales amount and get top 5
        sorted_products = sorted(
            product_sales.items(),
            key=lambda x: float(x[1]['amount']),
            reverse=True
        )[:5]

        best_selling_products = []
        for product_id, sales_data in sorted_products:
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                sku = f"PRD-{product.id:06d}"
                best_selling_products.append(BestSellingProduct(
                    product_id=str(product_id),
                    name=product.name,
                    sku=sku,
                    bnpl_sales_count=sales_data['count'],
                    bnpl_sales_amount=float(sales_data['amount'])
                ))

        return RetailerStats(
            retailer_id=str(retailer.id),
            currency="UGX",
            total_bnpl_sales=total_bnpl_sales,
            bnpl_transactions_30d=bnpl_transactions_30d,
            avg_ticket_size_30d=avg_ticket_size_30d,
            conversion_rate_30d=conversion_rate_30d,
            best_selling_products=best_selling_products,
            updated_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating retailer stats: {str(e)}"
        )


@router.get("/products", response_model=List[ProductResponse])
async def get_retailer_products_alias(
    current_user: User = Depends(require_role([UserRole.RETAILER])),
    db: Session = Depends(get_db),
):
    """Alias route: /retailer/products -> forwards to /products/retailer/products logic."""
    retailer = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer profile not found",
        )

    products = db.query(Product).filter(Product.retailer_id == retailer.id).all()
    return products


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_alias(
    product_data: ProductCreate,
    current_user: User = Depends(require_role([UserRole.RETAILER])),
    db: Session = Depends(get_db),
):
    """Alias route: /retailer/products (POST) -> forwards to /products/retailer/products logic."""
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


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product_alias(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_role([UserRole.RETAILER])),
    db: Session = Depends(get_db),
):
    """Alias route: /retailer/products/{id} (PUT) -> forwards to /products/retailer/products/{id} logic."""
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


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_alias(
    product_id: int,
    current_user: User = Depends(require_role([UserRole.RETAILER])),
    db: Session = Depends(get_db),
):
    """Alias route: /retailer/products/{id} (DELETE) -> forwards to /products/retailer/products/{id} logic."""
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

