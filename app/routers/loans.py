from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_active_user, require_role
from app.schemas.loan import LoanCreate, LoanResponse, LoanWithSchedules
from app.schemas.scoring import CreditScoreRequest
from app.models.user import User, UserRole
from app.models.loan import Loan, LoanStatus
from app.models.product import Product
from app.models.mfi import MFI
from app.services.payment_schedule import payment_schedule_service
from app.services.scoring import credit_scoring_service
from decimal import Decimal

router = APIRouter()


@router.post("/request", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def request_loan(
    loan_data: LoanCreate,
    current_user: User = Depends(require_role(UserRole.CUSTOMER)),
    db: Session = Depends(get_db),
):
    """Request a loan for a specific product."""
    # Get product
    product = db.query(Product).filter(Product.id == loan_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if not product.is_bnpl_eligible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not eligible for BNPL",
        )

    # Calculate credit score
    score_request = CreditScoreRequest(
        user_id=current_user.id,
        mobile_money_statement=None,  # Placeholder - should be uploaded/processed
        bank_statement=None,  # Placeholder - should be uploaded/processed
    )
    credit_score_response = credit_scoring_service.calculate_credit_score(db, score_request)

    # Find matching lender (simple matching logic)
    # Find MFI that matches credit score requirements
    matching_mfi = db.query(MFI).filter(
        MFI.is_active == True,
        MFI.min_credit_score <= credit_score_response.credit_score,
    ).first()

    if not matching_mfi:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No lender available for your credit score",
        )

    # Calculate loan amounts
    deposit_amount, loan_amount, total_amount = payment_schedule_service.calculate_loan_amounts(
        product_price=product.price,
        deposit_percentage=product.deposit_percentage,
        interest_rate=matching_mfi.interest_rate,
    )

    # Create loan
    db_loan = Loan(
        customer_id=current_user.id,
        lender_id=matching_mfi.id,
        product_id=product.id,
        loan_amount=loan_amount,
        deposit_amount=deposit_amount,
        total_amount=total_amount,
        interest_rate=matching_mfi.interest_rate,
        number_of_installments=loan_data.number_of_installments,
        status=LoanStatus.PENDING,
        credit_score=credit_score_response.credit_score,
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)

    return db_loan


@router.get("/my-loans", response_model=List[LoanResponse])
async def get_my_loans(
    current_user: User = Depends(require_role(UserRole.CUSTOMER)),
    db: Session = Depends(get_db),
):
    """Get all loans for the current customer."""
    loans = db.query(Loan).filter(Loan.customer_id == current_user.id).all()
    return loans


@router.get("/{loan_id}", response_model=LoanWithSchedules)
async def get_loan(
    loan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific loan with payment schedule."""
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )

    # Check permissions
    if current_user.role == UserRole.CUSTOMER and loan.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Generate payment schedule if loan is approved and schedule doesn't exist
    if loan.status == LoanStatus.APPROVED and not loan.payment_schedules:
        payment_schedule_service.generate_payment_schedule(db, loan)

    # Refresh to get payment schedules
    db.refresh(loan)

    return loan

