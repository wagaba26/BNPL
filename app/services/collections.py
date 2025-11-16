from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from app.models.loan import PaymentSchedule, PaymentStatus, Loan, LoanStatus
from app.models.user import User
from app.models.credit_profile import CreditProfile, CreditTier
from app.services.notification import notification_service
from app.services.scoring import CreditScoringService


class CollectionsService:
    """
    Collections and reminder service for managing installment reminders and overdue payments.
    """

    # Configuration constants
    REMINDER_DAYS_BEFORE_DUE = 3  # Send reminder 3 days before due date
    SEVERE_OVERDUE_DAYS = 30  # Consider severe overdue after 30 days
    CREDIT_SCORE_PENALTY_PER_OVERDUE = 10  # Points to deduct per overdue installment
    SEVERE_OVERDUE_PENALTY = 50  # Additional penalty for severe overdue

    @staticmethod
    def check_upcoming_installments(db: Session) -> List[PaymentSchedule]:
        """
        Check for installments that are due soon and mark them as REMINDER_DUE.
        
        Args:
            db: Database session
            
        Returns:
            List of PaymentSchedule objects marked as reminder due
        """
        now = datetime.utcnow()
        reminder_date = now + timedelta(days=CollectionsService.REMINDER_DAYS_BEFORE_DUE)
        
        # Find installments that are:
        # 1. Not yet paid
        # 2. Still pending or reminder_due status
        # 3. Due within the reminder window
        upcoming_installments = db.query(PaymentSchedule).join(Loan).filter(
            PaymentSchedule.status.in_([PaymentStatus.PENDING, PaymentStatus.REMINDER_DUE]),
            PaymentSchedule.due_date <= reminder_date,
            PaymentSchedule.due_date > now,
            Loan.status == LoanStatus.ACTIVE
        ).all()
        
        marked_installments = []
        for installment in upcoming_installments:
            if installment.status != PaymentStatus.REMINDER_DUE:
                installment.status = PaymentStatus.REMINDER_DUE
                installment.updated_at = now
                marked_installments.append(installment)
                
                # Send reminder notification
                loan = installment.loan
                user = loan.customer
                if user:
                    notification_service.send_reminder_notification(
                        user=user,
                        payment_schedule=installment,
                        loan=loan
                    )
        
        db.commit()
        return marked_installments

    @staticmethod
    def check_overdue_installments(db: Session) -> List[PaymentSchedule]:
        """
        Check for overdue installments, mark them as OVERDUE, send notifications,
        and update credit profiles for severe overdue cases.
        
        Args:
            db: Database session
            
        Returns:
            List of PaymentSchedule objects marked as overdue
        """
        now = datetime.utcnow()
        
        # Find installments that are:
        # 1. Not yet paid
        # 2. Due date has passed
        # 3. Loan is active
        overdue_installments = db.query(PaymentSchedule).join(Loan).filter(
            PaymentSchedule.status.in_([
                PaymentStatus.PENDING,
                PaymentStatus.REMINDER_DUE,
                PaymentStatus.OVERDUE
            ]),
            PaymentSchedule.due_date < now,
            Loan.status == LoanStatus.ACTIVE
        ).all()
        
        marked_installments = []
        user_penalties = {}  # Track penalties per user (only for newly overdue)
        
        for installment in overdue_installments:
            days_overdue = (now - installment.due_date).days
            was_already_overdue = installment.status == PaymentStatus.OVERDUE
            
            # Send notification if not already overdue (first time marking as overdue)
            # or if it's now severely overdue (even if previously overdue)
            should_notify = not was_already_overdue or (
                days_overdue >= CollectionsService.SEVERE_OVERDUE_DAYS and 
                installment.status == PaymentStatus.OVERDUE
            )
            
            if not was_already_overdue:
                installment.status = PaymentStatus.OVERDUE
                installment.updated_at = now
                marked_installments.append(installment)
            
            # Send overdue notification
            loan = installment.loan
            user = loan.customer
            if user and should_notify:
                if days_overdue >= CollectionsService.SEVERE_OVERDUE_DAYS:
                    # Severe overdue - send critical notification
                    notification_service.send_severe_overdue_notification(
                        user=user,
                        payment_schedule=installment,
                        loan=loan,
                        days_overdue=days_overdue
                    )
                    
                    # Track penalty for credit score update (only for newly overdue)
                    if not was_already_overdue:
                        if user.id not in user_penalties:
                            user_penalties[user.id] = {
                                'severely_overdue_count': 0,
                                'overdue_count': 0
                            }
                        user_penalties[user.id]['severely_overdue_count'] += 1
                else:
                    # Regular overdue notification
                    notification_service.send_overdue_notification(
                        user=user,
                        payment_schedule=installment,
                        loan=loan,
                        days_overdue=days_overdue
                    )
                    
                    # Track penalty for credit score update (only for newly overdue)
                    if not was_already_overdue:
                        if user.id not in user_penalties:
                            user_penalties[user.id] = {
                                'severely_overdue_count': 0,
                                'overdue_count': 0
                            }
                        user_penalties[user.id]['overdue_count'] += 1
        
        db.commit()
        
        # Update credit profiles for severe overdue cases
        if user_penalties:
            CollectionsService._update_credit_profiles_for_overdue(db, user_penalties)
        
        return marked_installments

    @staticmethod
    def _update_credit_profiles_for_overdue(
        db: Session,
        user_penalties: dict
    ) -> None:
        """
        Update credit profiles for users with overdue installments.
        Decreases credit score and possibly lowers tier.
        
        Args:
            db: Database session
            user_penalties: Dictionary mapping user_id to penalty counts
        """
        for user_id, penalties in user_penalties.items():
            credit_profile = db.query(CreditProfile).filter(
                CreditProfile.user_id == user_id
            ).first()
            
            if not credit_profile:
                # If no credit profile exists, create one first
                from app.schemas.scoring import CreditScoreRequest
                CreditScoringService.calculate_credit_score(
                    db,
                    CreditScoreRequest(user_id=user_id),
                    update_profile=True
                )
                credit_profile = db.query(CreditProfile).filter(
                    CreditProfile.user_id == user_id
                ).first()
            
            if credit_profile:
                # Calculate penalty
                penalty = 0
                if penalties['severely_overdue_count'] > 0:
                    # Severe overdue: apply SEVERE_OVERDUE_PENALTY for each
                    penalty += penalties['severely_overdue_count'] * CollectionsService.SEVERE_OVERDUE_PENALTY
                    # Also apply regular penalty
                    penalty += penalties['severely_overdue_count'] * CollectionsService.CREDIT_SCORE_PENALTY_PER_OVERDUE
                
                # Regular overdue (not severely overdue)
                regular_overdue = penalties['overdue_count'] - penalties['severely_overdue_count']
                if regular_overdue > 0:
                    penalty += regular_overdue * CollectionsService.CREDIT_SCORE_PENALTY_PER_OVERDUE
                
                # Update credit score
                new_score = max(0, credit_profile.score - penalty)
                credit_profile.score = new_score
                credit_profile.last_score_update = datetime.utcnow()
                
                # Recalculate tier based on new score
                credit_profile.tier = CreditScoringService._calculate_tier(new_score)
                
                # Recalculate max BNPL limit
                credit_profile.max_bnpl_limit = CreditScoringService._calculate_max_bnpl_limit(new_score)
                
                db.commit()
                db.refresh(credit_profile)
                
                print(
                    f"[COLLECTIONS] Updated credit profile for user {user_id}: "
                    f"score decreased by {penalty} to {new_score}, tier: {credit_profile.tier}"
                )

    @staticmethod
    def run_daily_collections_check(db: Session) -> dict:
        """
        Run the complete daily collections check.
        This method checks both upcoming and overdue installments.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with summary of collections check
        """
        try:
            upcoming = CollectionsService.check_upcoming_installments(db)
            overdue = CollectionsService.check_overdue_installments(db)
            
            return {
                "status": "success",
                "upcoming_installments_marked": len(upcoming),
                "overdue_installments_marked": len(overdue),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"[COLLECTIONS] Error during daily collections check: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


collections_service = CollectionsService()

