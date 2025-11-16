from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(15, 2), nullable=False)
    deposit_percentage = Column(Numeric(5, 2), nullable=False, default=0.00)  # e.g., 10.00 for 10%
    is_bnpl_eligible = Column(Boolean, default=True)
    min_required_score = Column(Integer, nullable=True)  # Minimum credit score required
    is_refurbished = Column(Boolean, default=False)  # Whether product is refurbished from trade-in
    category = Column(String, nullable=True)
    sku = Column(String, unique=True, index=True, nullable=True)
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    retailer = relationship("Retailer", back_populates="products")
    loans = relationship("Loan", back_populates="product")
    assets = relationship("UserAsset", back_populates="product")

    def __repr__(self):
        return f"<Product {self.name}>"

