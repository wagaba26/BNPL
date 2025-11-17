from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CreditScoreEvent(Base):
    __tablename__ = "credit_score_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)  # e.g., "DOCUMENT_APPROVED", "ON_TIME_PAYMENT", etc.
    delta = Column(Integer, nullable=False)  # Positive or negative score change
    score_before = Column(Integer, nullable=False)
    score_after = Column(Integer, nullable=False)
    event_metadata = Column(JSON, nullable=True)  # Extra details (e.g., document_id, loan_id, installment_id)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="credit_score_events")

    def __repr__(self):
        return f"<CreditScoreEvent user_id={self.user_id} type={self.event_type} delta={self.delta}>"

