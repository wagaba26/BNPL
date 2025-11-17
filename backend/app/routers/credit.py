"""
Credit Scoring API Router

Endpoints for credit profile, documents, and scoring events.
"""
import os
import uuid
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_role
from app.models import (
    User, UserRole, CreditProfile, CreditScoreEvent, CreditDocument,
    DocumentType, DocumentStatus
)
from app.schemas.credit import (
    CreditProfileResponse,
    CreditScoreEventResponse,
    CreditScoreEventListResponse,
    CreditDocumentResponse,
    CreditDocumentListResponse,
    DocumentReviewRequest,
    DocumentStatusSummary,
    DocumentStatusListResponse,
)
from app.services.credit_scoring import (
    get_or_create_credit_profile,
    handle_document_approved,
    recalculate_full_score,
)

router = APIRouter()

# File upload directory (create if doesn't exist)
UPLOAD_DIR = Path("uploads/credit_documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/profile/me", response_model=CreditProfileResponse)
async def get_my_credit_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's credit profile (CUSTOMER only).
    """
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers have credit profiles",
        )

    profile = get_or_create_credit_profile(db, current_user.id)
    return profile


@router.get("/events/me", response_model=CreditScoreEventListResponse)
async def get_my_credit_events(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get paginated list of credit score events for current user (CUSTOMER only).
    """
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can view their credit events",
        )

    # Calculate offset
    offset = (page - 1) * page_size

    # Query events
    events_query = db.query(CreditScoreEvent).filter(
        CreditScoreEvent.user_id == current_user.id
    ).order_by(desc(CreditScoreEvent.created_at))

    total = events_query.count()
    events = events_query.offset(offset).limit(page_size).all()

    return CreditScoreEventListResponse(
        events=[CreditScoreEventResponse.model_validate(e) for e in events],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/documents", response_model=CreditDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Upload a credit document (CUSTOMER only).
    
    Accepts multipart form data with:
    - document_type: One of the DocumentType enum values
    - file: The document file to upload
    """
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can upload documents",
        )

    # Generate unique filename
    file_ext = Path(file.filename).suffix if file.filename else ".pdf"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )

    # Create document record
    document = CreditDocument(
        user_id=current_user.id,
        document_type=document_type,
        file_path=str(file_path),
        status=DocumentStatus.PENDING,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@router.get("/documents/me", response_model=CreditDocumentListResponse)
async def get_my_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get list of all documents uploaded by current user (CUSTOMER only).
    """
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can view their documents",
        )

    documents = db.query(CreditDocument).filter(
        CreditDocument.user_id == current_user.id
    ).order_by(desc(CreditDocument.uploaded_at)).all()

    return CreditDocumentListResponse(
        documents=[CreditDocumentResponse.model_validate(d) for d in documents],
        total=len(documents),
    )


@router.get("/documents/status", response_model=DocumentStatusListResponse)
async def get_document_status_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get status summary for all document types (CUSTOMER only).
    
    Returns a checklist showing which documents have been uploaded and their status.
    """
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can view document status",
        )

    # Get all documents for user
    user_documents = db.query(CreditDocument).filter(
        CreditDocument.user_id == current_user.id
    ).all()

    # Create a map of document_type -> document
    doc_map = {doc.document_type: doc for doc in user_documents}

    # Build status summary for all document types
    summaries = []
    for doc_type in DocumentType:
        if doc_type in doc_map:
            doc = doc_map[doc_type]
            summaries.append(DocumentStatusSummary(
                document_type=doc_type.value,
                status=doc.status.value,
                document_id=doc.id,
                uploaded_at=doc.uploaded_at,
                reviewed_at=doc.reviewed_at,
            ))
        else:
            summaries.append(DocumentStatusSummary(
                document_type=doc_type.value,
                status=None,
                document_id=None,
                uploaded_at=None,
                reviewed_at=None,
            ))

    return DocumentStatusListResponse(documents=summaries)


@router.post("/documents/{document_id}/review", response_model=CreditDocumentResponse)
async def review_document(
    document_id: int,
    review_data: DocumentReviewRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """
    Review a document (APPROVE or REJECT) - ADMIN only.
    
    If approved, the credit score will be updated automatically.
    """
    document = db.query(CreditDocument).filter(CreditDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    previous_status = document.status
    document.status = review_data.status
    document.reviewed_at = datetime.now(timezone.utc)
    document.reviewer_id = current_user.id
    document.notes = review_data.notes

    # If approved, apply score change
    if review_data.status == DocumentStatus.APPROVED and previous_status != DocumentStatus.APPROVED:
        handle_document_approved(db, document)
    else:
        db.commit()
        db.refresh(document)

    return document


@router.post("/recalculate/me", response_model=CreditProfileResponse)
async def recalculate_my_score(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Recalculate credit score from scratch (CUSTOMER or ADMIN).
    
    This recomputes the score using all available data and current rules.
    """
    if current_user.role not in [UserRole.CUSTOMER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers and admins can recalculate scores",
        )

    profile = recalculate_full_score(db, current_user.id)
    return profile


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Download a document (CUSTOMER can download their own, ADMIN can download any).
    """
    document = db.query(CreditDocument).filter(CreditDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check permissions
    if current_user.role != UserRole.ADMIN and document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to download this document",
        )

    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server",
        )

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream",
    )

