from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from decimal import Decimal
from app.database import Base


class LoanStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"
    DEFAULTED = "defaulted"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    FAILED = "failed"
    REMINDER_DUE = "reminder_due"


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lender_id = Column(Integer, ForeignKey("mfis.id"), nullable=True)  # Nullable until matched
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    loan_amount = Column(Numeric(15, 2), nullable=False)  # Amount after deposit
    deposit_amount = Column(Numeric(15, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)  # Including interest
    interest_rate = Column(Numeric(5, 2), nullable=False)
    number_of_installments = Column(Integer, nullable=False, default=1)
    
    status = Column(SQLEnum(LoanStatus), default=LoanStatus.PENDING, nullable=False)
    credit_score = Column(Integer, nullable=True)
    
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("User", back_populates="loans", foreign_keys=[customer_id])
    lender = relationship("MFI", back_populates="loans", foreign_keys=[lender_id])
    product = relationship("Product", back_populates="loans")
    payment_schedules = relationship("PaymentSchedule", back_populates="loan", cascade="all, delete-orphan")
    asset = relationship("UserAsset", back_populates="loan", uselist=False)

    def __repr__(self):
        return f"<Loan {self.id} - {self.status}>"


class PaymentSchedule(Base):
    __tablename__ = "payment_schedules"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    installment_number = Column(Integer, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    payment_reference = Column(String, nullable=True)  # Reference from payment provider
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    loan = relationship("Loan", back_populates="payment_schedules")

    def __repr__(self):
        return f"<PaymentSchedule {self.installment_number} - {self.status}>"

