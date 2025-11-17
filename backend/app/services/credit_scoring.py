"""
Credit Scoring Service

This module contains the core credit scoring logic. It's designed to be modular
so that ML models can be plugged in later without breaking the API.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
import sqlalchemy as sa

from app.models import (
    User, CreditProfile, CreditScoreEvent, CreditDocument, 
    Loan, Installment, LoanStatus, DocumentType, DocumentStatus
)
from app.core.credit_config import (
    INITIAL_SCORE, INITIAL_TIER, INITIAL_MAX_BNPL_LIMIT,
    DOCUMENT_WEIGHTS, MAX_OTHER_DOCUMENT_POINTS,
    ON_TIME_PAYMENT_POINTS, MAX_ON_TIME_PAYMENT_POINTS,
    CONSECUTIVE_ON_TIME_STREAK_BONUS, STREAK_THRESHOLD,
    EARLY_REPAYMENT_BONUS_SMALL, EARLY_REPAYMENT_BONUS_MEDIUM, EARLY_REPAYMENT_BONUS_LARGE,
    EARLY_REPAYMENT_THRESHOLD_SMALL, EARLY_REPAYMENT_THRESHOLD_LARGE,
    LATE_PAYMENT_PENALTY, SEVERELY_LATE_PENALTY, DEFAULT_PENALTY,
    LATE_PAYMENT_DAYS, SEVERELY_LATE_DAYS,
    SUCCESSFUL_BNPL_PURCHASE_BONUS, MAX_USAGE_BONUS_POINTS,
    compute_tier_from_score, compute_limit_from_tier,
)


def get_or_create_credit_profile(db: Session, user_id: int) -> CreditProfile:
    """Get or create a credit profile for a user."""
    profile = db.query(CreditProfile).filter(CreditProfile.user_id == user_id).first()
    
    if not profile:
        profile = CreditProfile(
            user_id=user_id,
            score=INITIAL_SCORE,
            tier=INITIAL_TIER,
            max_bnpl_limit=INITIAL_MAX_BNPL_LIMIT,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile


def apply_score_change(
    db: Session,
    user_id: int,
    delta: int,
    event_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> CreditProfile:
    """
    Apply a score change and create an event record.
    
    Args:
        db: Database session
        user_id: User ID
        delta: Score change (positive or negative)
        event_type: Type of event (e.g., "DOCUMENT_APPROVED", "ON_TIME_PAYMENT")
        metadata: Optional metadata (e.g., document_id, loan_id)
    
    Returns:
        Updated CreditProfile
    """
    profile = get_or_create_credit_profile(db, user_id)
    
    score_before = profile.score
    score_after = max(0, min(1000, score_before + delta))  # Clamp to 0-1000
    
    # Update profile
    profile.score = score_after
    profile.tier = compute_tier_from_score(score_after)
    profile.max_bnpl_limit = compute_limit_from_tier(profile.tier)
    profile.updated_at = datetime.now(timezone.utc)
    
    # Create event
    event = CreditScoreEvent(
        user_id=user_id,
        event_type=event_type,
        delta=delta,
        score_before=score_before,
        score_after=score_after,
        event_metadata=metadata or {},
    )
    db.add(event)
    db.commit()
    db.refresh(profile)
    
    return profile


def handle_document_approved(db: Session, document: CreditDocument) -> CreditProfile:
    """
    Handle document approval and apply score change.
    
    Args:
        db: Database session
        document: Approved CreditDocument
    
    Returns:
        Updated CreditProfile
    """
    if document.status != DocumentStatus.APPROVED:
        raise ValueError("Document must be approved to apply score change")
    
    # Get document weight
    delta = DOCUMENT_WEIGHTS.get(document.document_type, 0)
    
    # Cap "OTHER" documents
    if document.document_type == DocumentType.OTHER:
        # Count existing OTHER document points
        existing_other_points = db.query(
            func.sum(CreditScoreEvent.delta)
        ).join(
            CreditDocument
        ).filter(
            and_(
                CreditScoreEvent.user_id == document.user_id,
                CreditScoreEvent.event_type == "DOCUMENT_APPROVED",
                CreditDocument.document_type == DocumentType.OTHER,
                CreditScoreEvent.id != None  # Placeholder for the new event
            )
        ).scalar() or 0
        
        # Only apply if under cap
        if existing_other_points >= MAX_OTHER_DOCUMENT_POINTS:
            delta = 0
    
    if delta > 0:
        return apply_score_change(
            db=db,
            user_id=document.user_id,
            delta=delta,
            event_type="DOCUMENT_APPROVED",
            metadata={"document_id": document.id, "document_type": document.document_type.value}
        )
    
    return get_or_create_credit_profile(db, document.user_id)


def handle_installment_payment(
    db: Session,
    installment: Installment,
    paid_at: Optional[datetime] = None
) -> CreditProfile:
    """
    Handle installment payment and apply score change based on timeliness.
    
    Args:
        db: Database session
        installment: Installment that was paid (must have loan relationship loaded)
        paid_at: Payment timestamp (defaults to now)
    
    Returns:
        Updated CreditProfile
    """
    if not installment.paid:
        raise ValueError("Installment must be marked as paid")
    
    # Ensure loan is loaded
    if not hasattr(installment, 'loan') or installment.loan is None:
        installment = db.query(Installment).options(
            sa.orm.joinedload(Installment.loan)
        ).filter(Installment.id == installment.id).first()
        if not installment:
            raise ValueError("Installment not found")
    
    customer_id = installment.loan.customer_id
    paid_at = paid_at or datetime.now(timezone.utc)
    
    # Calculate days overdue (negative if early)
    days_overdue = (paid_at.date() - installment.due_date.date()).days
    
    # Determine event type and delta
    if days_overdue <= 0:
        # On-time or early payment
        delta = ON_TIME_PAYMENT_POINTS
        
        # Check for consecutive on-time streak
        recent_events = db.query(CreditScoreEvent).filter(
            and_(
                CreditScoreEvent.user_id == customer_id,
                CreditScoreEvent.event_type == "ON_TIME_PAYMENT"
            )
        ).order_by(CreditScoreEvent.created_at.desc()).limit(STREAK_THRESHOLD - 1).all()
        
        if len(recent_events) >= STREAK_THRESHOLD - 1:
            # Check if they're consecutive (simplified check)
            delta += CONSECUTIVE_ON_TIME_STREAK_BONUS
        
        event_type = "ON_TIME_PAYMENT"
        
    elif days_overdue <= LATE_PAYMENT_DAYS:
        # Within grace period, no penalty
        return get_or_create_credit_profile(db, customer_id)
        
    elif days_overdue <= SEVERELY_LATE_DAYS:
        # Late payment
        delta = LATE_PAYMENT_PENALTY
        event_type = "LATE_PAYMENT"
        
    else:
        # Severely late
        delta = SEVERELY_LATE_PENALTY
        event_type = "SEVERELY_LATE_PAYMENT"
    
    return apply_score_change(
        db=db,
        user_id=customer_id,
        delta=delta,
        event_type=event_type,
        metadata={
            "installment_id": installment.id,
            "loan_id": installment.loan_id,
            "days_overdue": days_overdue
        }
    )


def handle_loan_status_change(
    db: Session,
    loan: Loan,
    previous_status: LoanStatus,
    new_status: LoanStatus
) -> Optional[CreditProfile]:
    """
    Handle loan status changes and apply score changes.
    
    Args:
        db: Database session
        loan: Loan with changed status
        previous_status: Previous loan status
        new_status: New loan status
    
    Returns:
        Updated CreditProfile or None if no change needed
    """
    if new_status == LoanStatus.PAID and previous_status == LoanStatus.ACTIVE:
        # Early full repayment bonus
        # Check if loan was paid early (simplified: check if all installments paid early)
        installments = db.query(Installment).filter(Installment.loan_id == loan.id).all()
        
        if installments:
            all_early = all(
                inst.paid and inst.paid_at and inst.paid_at.date() <= inst.due_date.date()
                for inst in installments
            )
            
            if all_early:
                # Determine bonus based on loan amount
                if loan.total_amount < EARLY_REPAYMENT_THRESHOLD_SMALL:
                    delta = EARLY_REPAYMENT_BONUS_SMALL
                elif loan.total_amount < EARLY_REPAYMENT_THRESHOLD_LARGE:
                    delta = EARLY_REPAYMENT_BONUS_MEDIUM
                else:
                    delta = EARLY_REPAYMENT_BONUS_LARGE
                
                return apply_score_change(
                    db=db,
                    user_id=loan.customer_id,
                    delta=delta,
                    event_type="EARLY_LOAN_REPAYMENT",
                    metadata={"loan_id": loan.id, "loan_amount": float(loan.total_amount)}
                )
    
    elif new_status == LoanStatus.DEFAULTED:
        # Default penalty
        return apply_score_change(
            db=db,
            user_id=loan.customer_id,
            delta=DEFAULT_PENALTY,
            event_type="LOAN_DEFAULT",
            metadata={"loan_id": loan.id, "loan_amount": float(loan.total_amount)}
        )
    
    return None


def recalculate_full_score(db: Session, user_id: int) -> CreditProfile:
    """
    Recalculate credit score from scratch using all available data.
    
    This allows us to change rules in the future and re-run scoring.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Updated CreditProfile
    """
    profile = get_or_create_credit_profile(db, user_id)
    
    # Start from initial score
    base_score = INITIAL_SCORE
    
    # 1. Document-based scoring (40% component)
    approved_documents = db.query(CreditDocument).filter(
        and_(
            CreditDocument.user_id == user_id,
            CreditDocument.status == DocumentStatus.APPROVED
        )
    ).all()
    
    document_points = 0
    other_document_points = 0
    
    for doc in approved_documents:
        points = DOCUMENT_WEIGHTS.get(doc.document_type, 0)
        
        if doc.document_type == DocumentType.OTHER:
            other_document_points += points
        else:
            document_points += points
    
    # Cap OTHER documents
    document_points += min(other_document_points, MAX_OTHER_DOCUMENT_POINTS)
    
    # 2. Repayment behavior scoring (40% component)
    # Count on-time payments
    on_time_events = db.query(CreditScoreEvent).filter(
        and_(
            CreditScoreEvent.user_id == user_id,
            CreditScoreEvent.event_type == "ON_TIME_PAYMENT"
        )
    ).count()
    
    repayment_points = min(on_time_events * ON_TIME_PAYMENT_POINTS, MAX_ON_TIME_PAYMENT_POINTS)
    
    # Count late payments
    late_events = db.query(CreditScoreEvent).filter(
        and_(
            CreditScoreEvent.user_id == user_id,
            CreditScoreEvent.event_type.in_(["LATE_PAYMENT", "SEVERELY_LATE_PAYMENT"])
        )
    ).count()
    
    repayment_points += late_events * LATE_PAYMENT_PENALTY
    
    # Count defaults
    default_events = db.query(CreditScoreEvent).filter(
        and_(
            CreditScoreEvent.user_id == user_id,
            CreditScoreEvent.event_type == "LOAN_DEFAULT"
        )
    ).count()
    
    repayment_points += default_events * DEFAULT_PENALTY
    
    # Early repayment bonuses
    early_repayment_events = db.query(CreditScoreEvent).filter(
        and_(
            CreditScoreEvent.user_id == user_id,
            CreditScoreEvent.event_type == "EARLY_LOAN_REPAYMENT"
        )
    ).all()
    
    for event in early_repayment_events:
        repayment_points += event.delta
    
    # 3. Usage & stability (20% component - simplified)
    # Count successful BNPL purchases (loans that were paid)
    successful_loans = db.query(Loan).filter(
        and_(
            Loan.customer_id == user_id,
            Loan.status == LoanStatus.PAID
        )
    ).count()
    
    usage_points = min(successful_loans * SUCCESSFUL_BNPL_PURCHASE_BONUS, MAX_USAGE_BONUS_POINTS)
    
    # Calculate final score
    # Note: In a real system, you might want to weight these components differently
    # For now, we'll use a simple additive model
    final_score = base_score + document_points + repayment_points + usage_points
    
    # Clamp to 0-1000
    final_score = max(0, min(1000, final_score))
    
    # Update profile
    profile.score = final_score
    profile.tier = compute_tier_from_score(final_score)
    profile.max_bnpl_limit = compute_limit_from_tier(profile.tier)
    profile.last_recalculated_at = datetime.now(timezone.utc)
    profile.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(profile)
    
    return profile

