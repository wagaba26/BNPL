from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class TradeInStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TradeInRequest(Base):
    __tablename__ = "trade_in_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("user_assets.id"), nullable=False)
    new_product_id = Column(Integer, ForeignKey("products.id"), nullable=True)  # Product they want to buy
    
    trade_in_value = Column(Numeric(15, 2), nullable=False)  # Calculated trade-in value
    new_product_price = Column(Numeric(15, 2), nullable=True)  # Price of new product if specified
    discount_applied = Column(Numeric(15, 2), nullable=True)  # Discount from trade-in value
    status = Column(SQLEnum(TradeInStatus), default=TradeInStatus.PENDING, nullable=False)
    
    notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="trade_in_requests")
    asset = relationship("UserAsset", back_populates="trade_in_requests")
    new_product = relationship("Product", foreign_keys=[new_product_id])

    def __repr__(self):
        return f"<TradeInRequest {self.id} - {self.status}>"


