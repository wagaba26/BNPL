from typing import List
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.models.lender import Lender
from app.models.product import Product
from app.models.loan import Loan, LoanStatus
from app.models.installment import Installment
from app.models.credit_profile import CreditProfile
from app.schemas.loan import BNPLRequest, LoanResponse, InstallmentResponse

router = APIRouter()


@router.post("/bnpl-requests", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_bnpl_request(
    request: BNPLRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a BNPL request (CUSTOMER only)."""
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can create BNPL requests",
        )

    # Get product
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Get customer's credit profile
    credit_profile = db.query(CreditProfile).filter(
        CreditProfile.user_id == current_user.id
    ).first()

    if not credit_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit profile not found",
        )

    # Validate eligibility
    if not product.bnpl_eligible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not BNPL eligible",
        )

    if product.min_required_score and credit_profile.score < product.min_required_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credit score too low for this product",
        )

    if product.price > credit_profile.max_bnpl_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product price exceeds maximum BNPL limit",
        )

    # Pick a lender (for now, just get the first active lender)
    lender = db.query(Lender).first()
    if not lender:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No lenders available",
        )

    # Calculate amounts
    deposit_amount = product.price * Decimal("0.20")  # 20% deposit
    principal_amount = product.price - deposit_amount

    # Calculate interest (simple interest, e.g., 10%)
    interest_rate = lender.base_interest_rate / Decimal("100")
    interest_amount = principal_amount * interest_rate
    total_amount = principal_amount + interest_amount

    # Create loan
    loan = Loan(
        customer_id=current_user.id,
        lender_id=lender.id,
        product_id=product.id,
        principal_amount=principal_amount,
        deposit_amount=deposit_amount,
        total_amount=total_amount,
        status=LoanStatus.ACTIVE,
    )
    db.add(loan)
    db.flush()

    # Generate installment schedule (3 installments, monthly)
    installment_amount = total_amount / Decimal("3")
    for i in range(3):
        due_date = datetime.utcnow() + timedelta(days=30 * (i + 1))
        installment = Installment(
            loan_id=loan.id,
            due_date=due_date,
            amount=installment_amount,
            paid=False,
        )
        db.add(installment)

    db.commit()
    db.refresh(loan)

    # Load installments
    installments = db.query(Installment).filter(Installment.loan_id == loan.id).all()

    return LoanResponse(
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
    )


@router.get("/me", response_model=List[LoanResponse])
async def get_my_loans(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current customer's loans."""
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can view their loans",
        )

    loans = db.query(Loan).filter(Loan.customer_id == current_user.id).all()

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


@router.get("/lender/loans", response_model=List[LoanResponse])
async def get_lender_loans(
    current_user: User = Depends(require_role([UserRole.LENDER])),
    db: Session = Depends(get_db),
):
    """Get loans for the current lender."""
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

