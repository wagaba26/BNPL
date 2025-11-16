from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from app.models.loan import LoanStatus, PaymentStatus


class LoanBase(BaseModel):
    product_id: int
    number_of_installments: int


class LoanCreate(LoanBase):
    pass


class LoanUpdate(BaseModel):
    status: Optional[LoanStatus] = None
    lender_id: Optional[int] = None
    rejection_reason: Optional[str] = None


class LoanApproval(BaseModel):
    loan_id: int
    approved: bool
    rejection_reason: Optional[str] = None


class LoanResponse(BaseModel):
    id: int
    customer_id: int
    lender_id: Optional[int] = None
    product_id: int
    loan_amount: Decimal
    deposit_amount: Decimal
    total_amount: Decimal
    interest_rate: Decimal
    number_of_installments: int
    status: LoanStatus
    credit_score: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Loan(LoanResponse):
    pass


class PaymentScheduleResponse(BaseModel):
    id: int
    loan_id: int
    installment_number: int
    due_date: datetime
    amount: Decimal
    status: PaymentStatus
    paid_at: Optional[datetime] = None
    payment_reference: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaymentSchedule(PaymentScheduleResponse):
    pass


class LoanWithSchedules(LoanResponse):
    payment_schedules: List[PaymentScheduleResponse] = []

