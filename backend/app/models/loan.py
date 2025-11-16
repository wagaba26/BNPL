from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class LoanStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    DEFAULTED = "DEFAULTED"


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lender_id = Column(Integer, ForeignKey("lenders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    principal_amount = Column(Numeric(15, 2), nullable=False)
    deposit_amount = Column(Numeric(15, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)  # principal + interest
    status = Column(SQLEnum(LoanStatus), default=LoanStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("User", back_populates="loans", foreign_keys=[customer_id])
    lender = relationship("Lender", back_populates="loans")
    product = relationship("Product", back_populates="loans")
    installments = relationship("Installment", back_populates="loan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Loan {self.id} - {self.status}>"

