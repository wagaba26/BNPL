from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_active_user
from app.schemas.loan import PaymentScheduleResponse
from app.models.user import User
from app.models.loan import PaymentSchedule, Loan

router = APIRouter()


@router.get("/my-payments", response_model=List[PaymentScheduleResponse])
async def get_my_payments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all payment schedules for the current user's loans."""
    # Get all loans for the user
    loans = db.query(Loan).filter(Loan.customer_id == current_user.id).all()
    loan_ids = [loan.id for loan in loans]

    # Get all payment schedules for these loans
    payments = db.query(PaymentSchedule).filter(
        PaymentSchedule.loan_id.in_(loan_ids)
    ).all()

    return payments


@router.get("/{payment_id}", response_model=PaymentScheduleResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific payment schedule."""
    payment = db.query(PaymentSchedule).filter(PaymentSchedule.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Check if payment belongs to user's loan
    loan = db.query(Loan).filter(Loan.id == payment.loan_id).first()
    if loan.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )

    return payment

