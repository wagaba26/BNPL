from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.loan import Loan, PaymentSchedule, PaymentStatus
from app.models.product import Product


class PaymentScheduleService:
    """Service for generating payment schedules for loans."""

    @staticmethod
    def calculate_loan_amounts(
        product_price: Decimal, deposit_percentage: Decimal, interest_rate: Decimal
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Calculate deposit, loan amount, and total amount with interest.
        Returns: (deposit_amount, loan_amount, total_amount)
        """
        deposit_amount = (product_price * deposit_percentage) / Decimal("100")
        loan_amount = product_price - deposit_amount
        interest_amount = (loan_amount * interest_rate) / Decimal("100")
        total_amount = loan_amount + interest_amount
        return deposit_amount, loan_amount, total_amount

    @staticmethod
    def generate_payment_schedule(
        db: Session,
        loan: Loan,
        start_date: Optional[datetime] = None,
    ) -> List[PaymentSchedule]:
        """
        Generate payment schedule for a loan.
        Creates equal monthly installments.
        """
        if start_date is None:
            start_date = datetime.utcnow()

        # Calculate installment amount
        installment_amount = loan.total_amount / Decimal(str(loan.number_of_installments))

        schedules = []
        for i in range(1, loan.number_of_installments + 1):
            # Calculate due date (monthly installments)
            # For simplicity, adding months by adding 30 days
            due_date = start_date + timedelta(days=30 * i)

            schedule = PaymentSchedule(
                loan_id=loan.id,
                installment_number=i,
                due_date=due_date,
                amount=installment_amount,
                status=PaymentStatus.PENDING,
            )
            schedules.append(schedule)
            db.add(schedule)

        db.commit()
        return schedules

    @staticmethod
    def mark_payment_as_paid(
        db: Session,
        schedule_id: int,
        payment_reference: str,
    ) -> PaymentSchedule:
        """Mark a payment schedule as paid and check if loan is completed."""
        schedule = db.query(PaymentSchedule).filter(PaymentSchedule.id == schedule_id).first()
        if not schedule:
            raise ValueError(f"Payment schedule with id {schedule_id} not found")

        schedule.status = PaymentStatus.PAID
        schedule.paid_at = datetime.utcnow()
        schedule.payment_reference = payment_reference

        # Check if all payments are paid
        loan = db.query(Loan).filter(Loan.id == schedule.loan_id).first()
        if loan:
            all_payments = db.query(PaymentSchedule).filter(
                PaymentSchedule.loan_id == loan.id
            ).all()
            
            all_paid = all(p.status == PaymentStatus.PAID for p in all_payments)
            
            if all_paid and loan.status != LoanStatus.COMPLETED:
                # Mark loan as completed
                loan.status = LoanStatus.COMPLETED
                
                # Create UserAsset
                PaymentScheduleService._create_user_asset(db, loan)
                
                # Update credit score
                PaymentScheduleService._update_credit_score_on_completion(db, loan)

        db.commit()
        db.refresh(schedule)
        return schedule

    @staticmethod
    def _create_user_asset(db: Session, loan: Loan):
        """Create a UserAsset when a loan is completed."""
        from app.models.user_asset import UserAsset
        
        # Check if asset already exists
        existing_asset = db.query(UserAsset).filter(UserAsset.loan_id == loan.id).first()
        if existing_asset:
            return
        
        # Get product info
        product = loan.product
        if not product:
            return
        
        asset = UserAsset(
            user_id=loan.customer_id,
            loan_id=loan.id,
            product_id=product.id,
            product_name=product.name,
            purchase_price=loan.total_amount + loan.deposit_amount,  # Total paid
            purchase_date=datetime.utcnow(),
            condition="new",
            is_traded_in=False
        )
        db.add(asset)

    @staticmethod
    def _update_credit_score_on_completion(db: Session, loan: Loan):
        """Update credit score when a loan is completed."""
        from app.services.scoring import credit_scoring_service
        from app.schemas.scoring import CreditScoreRequest
        
        # Recalculate credit score
        request = CreditScoreRequest(user_id=loan.customer_id)
        credit_scoring_service.calculate_credit_score(db, request, update_profile=True)


payment_schedule_service = PaymentScheduleService()

