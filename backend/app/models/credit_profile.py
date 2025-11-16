from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CreditProfile(Base):
    __tablename__ = "credit_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    score = Column(Integer, nullable=False, default=300)  # 0-1000
    tier = Column(String, nullable=False, default="TIER_1")  # e.g., "TIER_0", "TIER_1", etc.
    max_bnpl_limit = Column(Numeric(15, 2), nullable=False, default=200000.00)
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="credit_profile")

    def __repr__(self):
        return f"<CreditProfile user_id={self.user_id} score={self.score} tier={self.tier}>"

