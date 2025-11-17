from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class DocumentType(str, enum.Enum):
    MOBILE_MONEY_STATEMENT = "MOBILE_MONEY_STATEMENT"
    BANK_STATEMENT = "BANK_STATEMENT"
    PROOF_OF_ADDRESS = "PROOF_OF_ADDRESS"
    PAYSLIP = "PAYSLIP"
    EMPLOYMENT_CONTRACT = "EMPLOYMENT_CONTRACT"
    BUSINESS_REGISTRATION = "BUSINESS_REGISTRATION"
    LC1_LETTER = "LC1_LETTER"
    OTHER = "OTHER"


class DocumentStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class CreditDocument(Base):
    __tablename__ = "credit_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    file_path = Column(String, nullable=False)  # Path to stored file
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin who reviewed
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="credit_documents", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])

    def __repr__(self):
        return f"<CreditDocument id={self.id} type={self.document_type} status={self.status}>"

