from typing import Optional
from datetime import datetime
from app.models.loan import PaymentSchedule, Loan
from app.models.user import User


class NotificationService:
    """
    Notification service placeholder for SMS/WhatsApp integration.
    This service will be replaced with actual SMS/WhatsApp providers later.
    """

    @staticmethod
    def send_reminder_notification(
        user: User,
        payment_schedule: PaymentSchedule,
        loan: Loan
    ) -> bool:
        """
        Send reminder notification for upcoming installment.
        Placeholder implementation - replace with actual SMS/WhatsApp integration.
        
        Args:
            user: User who needs to be notified
            payment_schedule: Payment schedule that is due
            loan: Associated loan
            
        Returns:
            bool: True if notification was sent successfully (or would be sent)
        """
        # TODO: Integrate with SMS/WhatsApp provider
        # Example: twilio, africastalking, etc.
        message = (
            f"Reminder: Your installment #{payment_schedule.installment_number} "
            f"of {payment_schedule.amount} is due on {payment_schedule.due_date.strftime('%Y-%m-%d')}. "
            f"Loan ID: {loan.id}"
        )
        
        # Placeholder: Log the notification
        print(f"[NOTIFICATION] Sending reminder to {user.email} ({user.phone}): {message}")
        
        # In real implementation, this would call SMS/WhatsApp API
        # return sms_service.send(user.phone, message)
        
        return True

    @staticmethod
    def send_overdue_notification(
        user: User,
        payment_schedule: PaymentSchedule,
        loan: Loan,
        days_overdue: int
    ) -> bool:
        """
        Send overdue notification for missed installment.
        Placeholder implementation - replace with actual SMS/WhatsApp integration.
        
        Args:
            user: User who needs to be notified
            payment_schedule: Payment schedule that is overdue
            loan: Associated loan
            days_overdue: Number of days the installment is overdue
            
        Returns:
            bool: True if notification was sent successfully (or would be sent)
        """
        # TODO: Integrate with SMS/WhatsApp provider
        message = (
            f"URGENT: Your installment #{payment_schedule.installment_number} "
            f"of {payment_schedule.amount} is {days_overdue} day(s) overdue. "
            f"Please make payment immediately. Loan ID: {loan.id}"
        )
        
        # Placeholder: Log the notification
        print(f"[NOTIFICATION] Sending overdue alert to {user.email} ({user.phone}): {message}")
        
        # In real implementation, this would call SMS/WhatsApp API
        # return sms_service.send(user.phone, message)
        
        return True

    @staticmethod
    def send_severe_overdue_notification(
        user: User,
        payment_schedule: PaymentSchedule,
        loan: Loan,
        days_overdue: int
    ) -> bool:
        """
        Send severe overdue notification for long overdue installments.
        Placeholder implementation - replace with actual SMS/WhatsApp integration.
        
        Args:
            user: User who needs to be notified
            payment_schedule: Payment schedule that is severely overdue
            loan: Associated loan
            days_overdue: Number of days the installment is overdue
            
        Returns:
            bool: True if notification was sent successfully (or would be sent)
        """
        # TODO: Integrate with SMS/WhatsApp provider
        message = (
            f"CRITICAL: Your installment #{payment_schedule.installment_number} "
            f"of {payment_schedule.amount} is {days_overdue} day(s) overdue. "
            f"This may affect your credit score. Please contact us immediately. Loan ID: {loan.id}"
        )
        
        # Placeholder: Log the notification
        print(f"[NOTIFICATION] Sending severe overdue alert to {user.email} ({user.phone}): {message}")
        
        # In real implementation, this would call SMS/WhatsApp API
        # return sms_service.send(user.phone, message)
        
        return True


notification_service = NotificationService()

