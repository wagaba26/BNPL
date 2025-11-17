"""
Pydantic schemas for credit scoring endpoints.
"""
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.credit_document import DocumentType, DocumentStatus


# ============================================================================
# Credit Profile Schemas
# ============================================================================

class CreditProfileResponse(BaseModel):
    """Response schema for credit profile."""
    id: int
    user_id: int
    score: int = Field(..., ge=0, le=1000, description="Credit score from 0-1000")
    tier: str = Field(..., description="Credit tier (TIER_0 to TIER_4)")
    max_bnpl_limit: Decimal = Field(..., description="Maximum BNPL limit for this tier")
    last_recalculated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Credit Score Event Schemas
# ============================================================================

class CreditScoreEventResponse(BaseModel):
    """Response schema for credit score event."""
    id: int
    user_id: int
    event_type: str
    delta: int = Field(..., description="Score change (positive or negative)")
    score_before: int
    score_after: int
    event_metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both 'metadata' and 'event_metadata' in API


class CreditScoreEventListResponse(BaseModel):
    """Paginated list of credit score events."""
    events: List[CreditScoreEventResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Credit Document Schemas
# ============================================================================

class CreditDocumentResponse(BaseModel):
    """Response schema for credit document."""
    id: int
    user_id: int
    document_type: str
    file_path: str
    status: str
    uploaded_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class CreditDocumentListResponse(BaseModel):
    """List of credit documents."""
    documents: List[CreditDocumentResponse]
    total: int


class DocumentUploadRequest(BaseModel):
    """Request schema for document upload (multipart form)."""
    document_type: DocumentType
    # Note: file will be handled separately in the endpoint


class DocumentReviewRequest(BaseModel):
    """Request schema for document review."""
    status: DocumentStatus = Field(..., description="APPROVED or REJECTED")
    notes: Optional[str] = Field(None, max_length=1000, description="Review notes")


# ============================================================================
# Document Status Summary
# ============================================================================

class DocumentStatusSummary(BaseModel):
    """Summary of document upload status."""
    document_type: str
    status: Optional[str] = None  # None if not uploaded
    document_id: Optional[int] = None
    uploaded_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None


class DocumentStatusListResponse(BaseModel):
    """List of document status summaries."""
    documents: List[DocumentStatusSummary]

