from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional


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

