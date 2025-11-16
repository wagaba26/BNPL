from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.dependencies import get_current_active_user, require_role
from app.schemas.mfi import MFICreate, MFIUpdate, MFIResponse
from app.schemas.loan import LoanResponse, LoanApproval
from app.models.user import User, UserRole
from app.models.mfi import MFI
from app.models.loan import Loan, LoanStatus

router = APIRouter()


@router.post("/profile", response_model=MFIResponse, status_code=status.HTTP_201_CREATED)
async def create_mfi_profile(
    mfi_data: MFICreate,
    current_user: User = Depends(require_role(UserRole.LENDER)),
    db: Session = Depends(get_db),
):
    """Create or update MFI profile."""
    existing_mfi = db.query(MFI).filter(MFI.user_id == current_user.id).first()
    if existing_mfi:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFI profile already exists",
        )

    mfi_data.user_id = current_user.id
    db_mfi = MFI(**mfi_data.model_dump())
    db.add(db_mfi)
    db.commit()
    db.refresh(db_mfi)
    return db_mfi


@router.get("/profile", response_model=MFIResponse)
async def get_mfi_profile(
    current_user: User = Depends(require_role(UserRole.LENDER)),
    db: Session = Depends(get_db),
):
    """Get MFI profile."""
    mfi = db.query(MFI).filter(MFI.user_id == current_user.id).first()
    if not mfi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MFI profile not found",
        )
    return mfi


@router.put("/profile", response_model=MFIResponse)
async def update_mfi_profile(
    mfi_update: MFIUpdate,
    current_user: User = Depends(require_role(UserRole.LENDER)),
    db: Session = Depends(get_db),
):
    """Update MFI profile."""
    mfi = db.query(MFI).filter(MFI.user_id == current_user.id).first()
    if not mfi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MFI profile not found",
        )

    update_data = mfi_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(mfi, key, value)

    db.commit()
    db.refresh(mfi)
    return mfi


@router.get("/loans", response_model=List[LoanResponse])
async def list_loans(
    status_filter: LoanStatus | None = None,
    current_user: User = Depends(require_role(UserRole.LENDER)),
    db: Session = Depends(get_db),
):
    """List all loans for the current lender."""
    mfi = db.query(MFI).filter(MFI.user_id == current_user.id).first()
    if not mfi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MFI profile not found",
        )

    query = db.query(Loan).filter(Loan.lender_id == mfi.id)
    if status_filter:
        query = query.filter(Loan.status == status_filter)

    loans = query.all()
    return loans


@router.get("/loans/{loan_id}", response_model=LoanResponse)
async def get_loan(
    loan_id: int,
    current_user: User = Depends(require_role(UserRole.LENDER)),
    db: Session = Depends(get_db),
):
    """Get a specific loan."""
    mfi = db.query(MFI).filter(MFI.user_id == current_user.id).first()
    if not mfi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MFI profile not found",
        )

    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.lender_id == mfi.id,
    ).first()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )
    return loan


@router.post("/loans/{loan_id}/approve", response_model=LoanResponse)
async def approve_loan(
    loan_id: int,
    approval: LoanApproval,
    current_user: User = Depends(require_role(UserRole.LENDER)),
    db: Session = Depends(get_db),
):
    """Approve or reject a loan."""
    mfi = db.query(MFI).filter(MFI.user_id == current_user.id).first()
    if not mfi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MFI profile not found",
        )

    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.lender_id == mfi.id,
    ).first()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )

    if approval.approved:
        loan.status = LoanStatus.APPROVED
        loan.approved_at = datetime.utcnow()
        loan.rejection_reason = None
    else:
        loan.status = LoanStatus.REJECTED
        loan.rejected_at = datetime.utcnow()
        loan.rejection_reason = approval.rejection_reason

    db.commit()
    db.refresh(loan)
    return loan

