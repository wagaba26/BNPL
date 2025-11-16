from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from app.models.loan import LoanStatus


class BNPLRequest(BaseModel):
    product_id: int


class InstallmentResponse(BaseModel):
    id: int
    loan_id: int
    due_date: datetime
    amount: Decimal
    paid: bool
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True


class LoanResponse(BaseModel):
    id: int
    customer_id: int
    lender_id: int
    product_id: int
    principal_amount: Decimal
    deposit_amount: Decimal
    total_amount: Decimal
    status: LoanStatus
    created_at: datetime
    installments: List[InstallmentResponse] = []

    class Config:
        from_attributes = True

