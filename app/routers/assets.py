from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from app.database import get_db
from app.dependencies import get_current_active_user, require_role
from app.schemas.user_asset import UserAssetResponse
from app.schemas.trade_in import TradeInRequestCreate, TradeInRequestResponse
from app.models.user import User, UserRole
from app.models.user_asset import UserAsset
from app.models.trade_in import TradeInRequest, TradeInStatus
from app.models.product import Product
from app.models.loan import Loan, LoanStatus

router = APIRouter()


@router.get("/my-assets", response_model=List[UserAssetResponse])
async def list_my_assets(
    current_user: User = Depends(require_role(UserRole.CUSTOMER)),
    db: Session = Depends(get_db),
):
    """List all assets owned by the current user."""
    assets = db.query(UserAsset).filter(
        UserAsset.user_id == current_user.id,
        UserAsset.is_traded_in == False
    ).all()
    return assets


@router.get("/my-assets/{asset_id}", response_model=UserAssetResponse)
async def get_asset(
    asset_id: int,
    current_user: User = Depends(require_role(UserRole.CUSTOMER)),
    db: Session = Depends(get_db),
):
    """Get a specific asset."""
    asset = db.query(UserAsset).filter(UserAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    if asset.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return asset


def _calculate_trade_in_value(asset: UserAsset) -> Decimal:
    """Calculate trade-in value based on asset condition and age."""
    # Simple calculation: depreciate by 30% per year, with condition adjustments
    from datetime import datetime
    age_years = (datetime.utcnow() - asset.purchase_date).days / 365.0
    
    # Base depreciation: 30% per year, capped at 70% total
    depreciation_rate = min(0.30 * age_years, 0.70)
    base_value = asset.purchase_price * (1 - Decimal(str(depreciation_rate)))
    
    # Condition adjustments
    condition_multipliers = {
        "new": Decimal("1.0"),
        "excellent": Decimal("0.85"),
        "good": Decimal("0.70"),
        "fair": Decimal("0.50"),
        "poor": Decimal("0.30"),
    }
    
    condition = asset.condition or "good"
    multiplier = condition_multipliers.get(condition.lower(), Decimal("0.70"))
    
    trade_in_value = base_value * multiplier
    return max(trade_in_value, Decimal("0"))  # Ensure non-negative


@router.post("/trade-in", response_model=TradeInRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_trade_in_request(
    trade_in_data: TradeInRequestCreate,
    current_user: User = Depends(require_role(UserRole.CUSTOMER)),
    db: Session = Depends(get_db),
):
    """Create a trade-in request for an asset."""
    # Verify asset belongs to user
    asset = db.query(UserAsset).filter(UserAsset.id == trade_in_data.asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    if asset.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Asset does not belong to you",
        )
    
    if asset.is_traded_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset has already been traded in",
        )
    
    # Calculate trade-in value
    trade_in_value = _calculate_trade_in_value(asset)
    
    # Get new product price if specified
    new_product_price = None
    if trade_in_data.new_product_id:
        new_product = db.query(Product).filter(Product.id == trade_in_data.new_product_id).first()
        if not new_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New product not found",
            )
        new_product_price = new_product.price
    
    # Create trade-in request
    trade_in_request = TradeInRequest(
        user_id=current_user.id,
        asset_id=asset.id,
        new_product_id=trade_in_data.new_product_id,
        trade_in_value=trade_in_value,
        new_product_price=new_product_price,
        discount_applied=trade_in_value if new_product_price else None,
        status=TradeInStatus.PENDING,
        notes=trade_in_data.notes,
    )
    
    db.add(trade_in_request)
    db.commit()
    db.refresh(trade_in_request)
    
    return trade_in_request


@router.get("/trade-in/my-requests", response_model=List[TradeInRequestResponse])
async def list_my_trade_in_requests(
    current_user: User = Depends(require_role(UserRole.CUSTOMER)),
    db: Session = Depends(get_db),
):
    """List all trade-in requests for the current user."""
    requests = db.query(TradeInRequest).filter(
        TradeInRequest.user_id == current_user.id
    ).all()
    return requests


@router.get("/trade-in/{request_id}", response_model=TradeInRequestResponse)
async def get_trade_in_request(
    request_id: int,
    current_user: User = Depends(require_role(UserRole.CUSTOMER)),
    db: Session = Depends(get_db),
):
    """Get a specific trade-in request."""
    request = db.query(TradeInRequest).filter(TradeInRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade-in request not found",
        )
    
    if request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return request


