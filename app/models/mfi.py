from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MFI(Base):
    __tablename__ = "mfis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    institution_name = Column(String, nullable=False)
    registration_number = Column(String, unique=True, index=True, nullable=True)
    interest_rate = Column(Numeric(5, 2), nullable=False, default=0.00)  # Annual interest rate
    max_loan_amount = Column(Numeric(15, 2), nullable=True)
    min_credit_score = Column(Integer, nullable=True, default=0)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="mfi_profile")
    loans = relationship("Loan", back_populates="lender", foreign_keys="Loan.lender_id")

    def __repr__(self):
        return f"<MFI {self.institution_name}>"

