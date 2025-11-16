from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class CreditTier(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class CreditProfile(Base):
    __tablename__ = "credit_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    score = Column(Integer, nullable=False, default=0)  # 0-1000
    tier = Column(SQLEnum(CreditTier), default=CreditTier.BRONZE, nullable=False)
    max_bnpl_limit = Column(Numeric(15, 2), nullable=False, default=0.00)
    last_score_update = Column(DateTime(timezone=True), server_default=func.now())
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="credit_profile", uselist=False)

    def __repr__(self):
        return f"<CreditProfile user_id={self.user_id} score={self.score} tier={self.tier}>"


