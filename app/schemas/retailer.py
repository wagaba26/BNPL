from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class RetailerBase(BaseModel):
    business_name: str
    registration_number: Optional[str] = None
    business_address: Optional[str] = None


class RetailerCreate(RetailerBase):
    user_id: int


class RetailerUpdate(BaseModel):
    business_name: Optional[str] = None
    registration_number: Optional[str] = None
    business_address: Optional[str] = None


class RetailerResponse(RetailerBase):
    id: int
    user_id: int
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Retailer(RetailerResponse):
    pass

