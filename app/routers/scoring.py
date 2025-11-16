from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User, UserRole
from app.schemas.scoring import CreditScoreRequest, CreditScoreResponse
from app.services.scoring import credit_scoring_service

router = APIRouter()


@router.post("/calculate", response_model=CreditScoreResponse)
async def calculate_credit_score(
    score_request: CreditScoreRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Calculate credit score for a user. Updates credit profile when documents are uploaded."""
    # Check if user is requesting their own score or is admin
    if score_request.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )

    try:
        result = credit_scoring_service.calculate_credit_score(db, score_request, update_profile=True)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

