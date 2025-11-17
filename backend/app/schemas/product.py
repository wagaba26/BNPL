from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    bnpl_eligible: bool = True
    min_required_score: Optional[int] = None
    stock: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    bnpl_eligible: Optional[bool] = None
    min_required_score: Optional[int] = None
    stock: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    retailer_id: int
    name: str
    description: Optional[str]
    price: Decimal
    bnpl_eligible: bool
    min_required_score: Optional[int]
    stock: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Detailed product response for checkout
class ProductPrice(BaseModel):
    currency: str
    amount: float


class ProductBNPL(BaseModel):
    eligible: bool
    min_deposit_percent: float
    max_tenure_months: int
    interest_rate_percent_per_month: float


class ProductStock(BaseModel):
    available_quantity: int
    is_active: bool


class ProductRetailer(BaseModel):
    id: str
    name: str


class ProductDetailResponse(BaseModel):
    id: str
    name: str
    sku: str
    description: str
    price: ProductPrice
    bnpl: ProductBNPL
    stock: ProductStock
    retailer: ProductRetailer
    images: List[str]
    created_at: str
    updated_at: str

