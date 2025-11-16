from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Lender(Base):
    __tablename__ = "lenders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    institution_name = Column(String, nullable=False)
    max_loan_amount = Column(Numeric(15, 2), nullable=True)
    base_interest_rate = Column(Numeric(5, 2), nullable=False, default=10.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="lender_profile")
    loans = relationship("Loan", back_populates="lender")

    def __repr__(self):
        return f"<Lender {self.institution_name}>"

