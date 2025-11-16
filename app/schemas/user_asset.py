from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal


class UserAssetBase(BaseModel):
    product_name: str
    purchase_price: Decimal
    condition: Optional[str] = None
    notes: Optional[str] = None


class UserAssetCreate(UserAssetBase):
    loan_id: int
    product_id: int


class UserAssetResponse(UserAssetBase):
    id: int
    user_id: int
    loan_id: int
    product_id: int
    purchase_date: datetime
    is_traded_in: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserAsset(UserAssetResponse):
    pass


