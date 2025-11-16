from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(15, 2), nullable=False)
    bnpl_eligible = Column(Boolean, default=True)
    min_required_score = Column(Integer, nullable=True)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    retailer = relationship("Retailer", back_populates="products")
    loans = relationship("Loan", back_populates="product")

    def __repr__(self):
        return f"<Product {self.name}>"

