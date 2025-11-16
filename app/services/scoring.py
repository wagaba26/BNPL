from typing import Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from app.schemas.scoring import CreditScoreRequest, CreditScoreResponse
from app.models.user import User
from app.models.credit_profile import CreditProfile, CreditTier


class CreditScoringService:
    """Credit scoring service stub that can be replaced with a real implementation later."""

    @staticmethod
    def _calculate_tier(score: int) -> CreditTier:
        """Determine credit tier based on score."""
        if score >= 800:
            return CreditTier.PLATINUM
        elif score >= 650:
            return CreditTier.GOLD
        elif score >= 500:
            return CreditTier.SILVER
        else:
            return CreditTier.BRONZE

    @staticmethod
    def _calculate_max_bnpl_limit(score: int) -> Decimal:
        """Calculate max BNPL limit based on credit score."""
        # Simple calculation: score * 10 (e.g., 500 score = 5000 limit)
        # Can be made more sophisticated
        base_limit = Decimal(score) * Decimal("10")
        # Cap at reasonable maximum
        return min(base_limit, Decimal("50000"))

    @staticmethod
    def calculate_credit_score(
        db: Session, request: CreditScoreRequest, update_profile: bool = True
    ) -> CreditScoreResponse:
        """
        Calculate credit score based on user data and update CreditProfile.
        This is a stub implementation that returns a mock score.
        Replace with actual scoring logic (ML model, external API, etc.)
        """
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise ValueError(f"User with id {request.user_id} not found")

        # Get existing credit profile or create new one
        credit_profile = db.query(CreditProfile).filter(
            CreditProfile.user_id == request.user_id
        ).first()

        # Stub scoring logic
        base_score = 500
        
        # Mock factors
        factors = {
            "base_score": base_score,
            "has_mobile_money_statement": request.mobile_money_statement is not None,
            "has_bank_statement": request.bank_statement is not None,
            "has_documents": request.documents is not None,
        }

        # Simple mock adjustments
        if request.mobile_money_statement:
            base_score += 100
        if request.bank_statement:
            base_score += 150
        if request.documents:
            base_score += 50
        if user.is_verified:
            base_score += 100

        # If user has completed loans, add bonus
        from app.models.loan import Loan, LoanStatus
        completed_loans = db.query(Loan).filter(
            Loan.customer_id == request.user_id,
            Loan.status == LoanStatus.COMPLETED
        ).count()
        if completed_loans > 0:
            base_score += min(completed_loans * 20, 100)  # Up to 100 points for loan history
            factors["completed_loans"] = completed_loans

        # Cap score between 0 and 1000
        score = max(0, min(1000, base_score))

        # Determine risk level
        if score >= 700:
            risk_level = "low"
        elif score >= 500:
            risk_level = "medium"
        else:
            risk_level = "high"

        factors["final_score"] = score

        # Update or create CreditProfile
        if update_profile:
            tier = CreditScoringService._calculate_tier(score)
            max_limit = CreditScoringService._calculate_max_bnpl_limit(score)
            
            if credit_profile:
                credit_profile.score = score
                credit_profile.tier = tier
                credit_profile.max_bnpl_limit = max_limit
                credit_profile.last_score_update = datetime.utcnow()
            else:
                credit_profile = CreditProfile(
                    user_id=request.user_id,
                    score=score,
                    tier=tier,
                    max_bnpl_limit=max_limit,
                    last_score_update=datetime.utcnow()
                )
                db.add(credit_profile)
            
            db.commit()
            db.refresh(credit_profile)

        return CreditScoreResponse(
            user_id=request.user_id,
            credit_score=score,
            risk_level=risk_level,
            factors=factors,
        )

    @staticmethod
    def get_or_create_credit_profile(db: Session, user_id: int) -> CreditProfile:
        """Get existing credit profile or create one with initial score."""
        credit_profile = db.query(CreditProfile).filter(
            CreditProfile.user_id == user_id
        ).first()
        
        if not credit_profile:
            # Create initial credit profile
            request = CreditScoreRequest(user_id=user_id)
            CreditScoringService.calculate_credit_score(db, request, update_profile=True)
            db.refresh(credit_profile)
            credit_profile = db.query(CreditProfile).filter(
                CreditProfile.user_id == user_id
            ).first()
        
        return credit_profile


credit_scoring_service = CreditScoringService()

