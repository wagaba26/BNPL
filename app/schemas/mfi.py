from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal


class MFIBase(BaseModel):
    institution_name: str
    registration_number: Optional[str] = None
    interest_rate: Decimal
    max_loan_amount: Optional[Decimal] = None
    min_credit_score: Optional[int] = None


class MFICreate(MFIBase):
    user_id: int


class MFIUpdate(BaseModel):
    institution_name: Optional[str] = None
    registration_number: Optional[str] = None
    interest_rate: Optional[Decimal] = None
    max_loan_amount: Optional[Decimal] = None
    min_credit_score: Optional[int] = None
    is_active: Optional[bool] = None


class MFIResponse(MFIBase):
    id: int
    user_id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MFI(MFIResponse):
    pass

