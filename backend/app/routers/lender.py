from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.models.lender import Lender
from app.models.loan import Loan, LoanStatus
from app.models.installment import Installment
from app.schemas.loan import LoanResponse, InstallmentResponse
from pydantic import BaseModel


router = APIRouter()


class AgingBuckets(BaseModel):
    current: int
    late_1_30: int
    late_31_60: int
    late_61_plus: int


class LenderStats(BaseModel):
    lender_id: str
    active_loans_count: int
    total_principal_outstanding: float
    total_interest_earned: float
    currency: str
    aging_buckets: AgingBuckets
    updated_at: str


@router.get("/stats", response_model=LenderStats)
async def get_lender_stats(
    current_user: User = Depends(require_role([UserRole.LENDER])),
    db: Session = Depends(get_db),
):
    """Get lender dashboard statistics."""
    try:
        # Get lender profile
        lender = db.query(Lender).filter(Lender.user_id == current_user.id).first()
        if not lender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lender profile not found",
            )

        # Get all loans for this lender
        loans = db.query(Loan).filter(Loan.lender_id == lender.id).all()

        # Calculate active loans count
        active_loans = [loan for loan in loans if loan.status == LoanStatus.ACTIVE]
        active_loans_count = len(active_loans)

        # Calculate total principal outstanding (sum of principal_amount for active loans)
        total_principal_outstanding = sum(
            float(loan.principal_amount) for loan in active_loans
        )

        # Calculate total interest earned
        # Interest = total_amount - principal_amount for all loans (including completed)
        total_interest_earned = sum(
            float(loan.total_amount - loan.principal_amount) for loan in loans
        )

        # Calculate aging buckets based on installments
        now = datetime.utcnow()
        current_count = 0
        late_1_30 = 0
        late_31_60 = 0
        late_61_plus = 0

        for loan in active_loans:
            # Get unpaid installments for this loan
            unpaid_installments = db.query(Installment).filter(
                and_(
                    Installment.loan_id == loan.id,
                    Installment.paid == False
                )
            ).all()

            for installment in unpaid_installments:
                days_overdue = (now - installment.due_date).days
                
                if days_overdue < 0:
                    # Not yet due
                    current_count += 1
                elif days_overdue <= 30:
                    late_1_30 += 1
                elif days_overdue <= 60:
                    late_31_60 += 1
                else:
                    late_61_plus += 1

        return LenderStats(
            lender_id=str(lender.id),
            active_loans_count=active_loans_count,
            total_principal_outstanding=total_principal_outstanding,
            total_interest_earned=total_interest_earned,
            currency="UGX",  # Default currency
            aging_buckets=AgingBuckets(
                current=current_count,
                late_1_30=late_1_30,
                late_31_60=late_31_60,
                late_61_plus=late_61_plus
            ),
            updated_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating lender stats: {str(e)}"
        )


@router.get("/loans", response_model=List[LoanResponse])
async def get_lender_loans_alias(
    current_user: User = Depends(require_role([UserRole.LENDER])),
    db: Session = Depends(get_db),
):
    """Alias route: /lender/loans -> forwards to /loans/lender/loans logic."""
    # Get lender profile
    lender = db.query(Lender).filter(Lender.user_id == current_user.id).first()
    if not lender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lender profile not found",
        )

    loans = db.query(Loan).filter(Loan.lender_id == lender.id).all()

    result = []
    for loan in loans:
        installments = db.query(Installment).filter(Installment.loan_id == loan.id).all()
        result.append(LoanResponse(
            id=loan.id,
            customer_id=loan.customer_id,
            lender_id=loan.lender_id,
            product_id=loan.product_id,
            principal_amount=loan.principal_amount,
            deposit_amount=loan.deposit_amount,
            total_amount=loan.total_amount,
            status=loan.status,
            created_at=loan.created_at,
            installments=[InstallmentResponse(
                id=inst.id,
                loan_id=inst.loan_id,
                due_date=inst.due_date,
                amount=inst.amount,
                paid=inst.paid,
                paid_at=inst.paid_at,
            ) for inst in installments],
        ))

    return result

