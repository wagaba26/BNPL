from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    deposit_percentage: Decimal
    is_bnpl_eligible: bool = True
    min_required_score: Optional[int] = None
    is_refurbished: bool = False
    category: Optional[str] = None
    sku: Optional[str] = None
    stock_quantity: int = 0


class ProductCreate(ProductBase):
    retailer_id: int


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    deposit_percentage: Optional[Decimal] = None
    is_bnpl_eligible: Optional[bool] = None
    min_required_score: Optional[int] = None
    is_refurbished: Optional[bool] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    retailer_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Product(ProductResponse):
    pass

