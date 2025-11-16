from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    RETAILER = "retailer"
    LENDER = "lender"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    nin = Column(String, unique=True, index=True, nullable=True)  # National ID
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    loans = relationship("Loan", back_populates="customer", foreign_keys="Loan.customer_id")
    retailer_profile = relationship("Retailer", back_populates="user", uselist=False)
    mfi_profile = relationship("MFI", back_populates="user", uselist=False)
    credit_profile = relationship("CreditProfile", back_populates="user", uselist=False)
    assets = relationship("UserAsset", back_populates="user")
    trade_in_requests = relationship("TradeInRequest", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"

