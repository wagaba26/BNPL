from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserAsset(Base):
    __tablename__ = "user_assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False, unique=True)  # One asset per completed loan
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    product_name = Column(String, nullable=False)  # Snapshot of product name at time of purchase
    purchase_price = Column(Numeric(15, 2), nullable=False)  # Original purchase price
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    condition = Column(String, nullable=True)  # e.g., "new", "excellent", "good", "fair"
    notes = Column(Text, nullable=True)
    is_traded_in = Column(Boolean, default=False)  # Whether this asset has been traded in
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="assets")
    loan = relationship("Loan", back_populates="asset")
    product = relationship("Product", back_populates="assets")
    trade_in_requests = relationship("TradeInRequest", back_populates="asset")

    def __repr__(self):
        return f"<UserAsset {self.id} - {self.product_name}>"


