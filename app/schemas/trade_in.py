from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal
from app.models.trade_in import TradeInStatus


class TradeInRequestBase(BaseModel):
    asset_id: int
    new_product_id: Optional[int] = None
    notes: Optional[str] = None


class TradeInRequestCreate(TradeInRequestBase):
    pass


class TradeInRequestResponse(BaseModel):
    id: int
    user_id: int
    asset_id: int
    new_product_id: Optional[int] = None
    trade_in_value: Decimal
    new_product_price: Optional[Decimal] = None
    discount_applied: Optional[Decimal] = None
    status: TradeInStatus
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TradeInRequest(TradeInRequestResponse):
    pass


