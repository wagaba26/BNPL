from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.models.credit_profile import CreditProfile
from app.schemas.credit_profile import CreditProfileResponse

router = APIRouter()


@router.get("/me", response_model=CreditProfileResponse)
async def get_my_credit_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current user's credit profile (CUSTOMER only)."""
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers have credit profiles",
        )

    credit_profile = db.query(CreditProfile).filter(
        CreditProfile.user_id == current_user.id
    ).first()

    if not credit_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit profile not found",
        )

    return credit_profile

