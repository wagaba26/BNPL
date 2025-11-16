from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Installment(Base):
    __tablename__ = "installments"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    paid = Column(Boolean, default=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    loan = relationship("Loan", back_populates="installments")

    def __repr__(self):
        return f"<Installment {self.id} - {self.due_date}>"

