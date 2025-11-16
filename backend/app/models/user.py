from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    RETAILER = "RETAILER"
    LENDER = "LENDER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    retailer_profile = relationship("Retailer", back_populates="user", uselist=False)
    lender_profile = relationship("Lender", back_populates="user", uselist=False)
    credit_profile = relationship("CreditProfile", back_populates="user", uselist=False)
    loans = relationship("Loan", back_populates="customer", foreign_keys="Loan.customer_id")

    def __repr__(self):
        return f"<User {self.email}>"

