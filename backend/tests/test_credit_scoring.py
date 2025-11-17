"""
Tests for credit scoring functionality.
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal, Base, engine
from app.models import (
    User, UserRole, CreditProfile, CreditScoreEvent, CreditDocument,
    Loan, Installment, LoanStatus, DocumentType, DocumentStatus
)
from app.core.security import get_password_hash
from app.services.credit_scoring import (
    get_or_create_credit_profile,
    apply_score_change,
    handle_document_approved,
    handle_installment_payment,
    handle_loan_status_change,
    recalculate_full_score,
)
from app.core.credit_config import (
    INITIAL_SCORE, INITIAL_TIER, INITIAL_MAX_BNPL_LIMIT,
    DOCUMENT_WEIGHTS, compute_tier_from_score, compute_limit_from_tier,
)

# Create test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture
def db():
    """Create a test database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def test_customer(db: Session):
    """Create a test customer user."""
    user = User(
        name="Test Customer",
        email="customer@test.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.CUSTOMER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db: Session):
    """Create a test admin user."""
    user = User(
        name="Test Admin",
        email="admin@test.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_token_customer(test_customer):
    """Get auth token for test customer."""
    response = client.post(
        "/auth/login",
        json={
            "email": "customer@test.com",
            "password": "password123",
        },
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_token_admin(test_admin):
    """Get auth token for test admin."""
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@test.com",
            "password": "password123",
        },
    )
    return response.json()["access_token"]


class TestCreditProfile:
    """Tests for credit profile creation and retrieval."""

    def test_get_or_create_credit_profile(self, db: Session, test_customer):
        """Test creating a credit profile."""
        profile = get_or_create_credit_profile(db, test_customer.id)
        
        assert profile is not None
        assert profile.user_id == test_customer.id
        assert profile.score == INITIAL_SCORE
        assert profile.tier == INITIAL_TIER
        assert profile.max_bnpl_limit == INITIAL_MAX_BNPL_LIMIT

    def test_get_existing_credit_profile(self, db: Session, test_customer):
        """Test retrieving an existing credit profile."""
        # Create profile first
        profile1 = get_or_create_credit_profile(db, test_customer.id)
        
        # Get it again
        profile2 = get_or_create_credit_profile(db, test_customer.id)
        
        assert profile1.id == profile2.id
        assert profile2.score == INITIAL_SCORE


class TestDocumentScoring:
    """Tests for document-based scoring."""

    def test_document_approval_increases_score(self, db: Session, test_customer):
        """Test that approving a document increases credit score."""
        profile = get_or_create_credit_profile(db, test_customer.id)
        initial_score = profile.score
        
        # Create and approve a document
        document = CreditDocument(
            user_id=test_customer.id,
            document_type=DocumentType.BANK_STATEMENT,
            file_path="/test/path.pdf",
            status=DocumentStatus.PENDING,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Approve it
        document.status = DocumentStatus.APPROVED
        updated_profile = handle_document_approved(db, document)
        
        # Check score increased
        assert updated_profile.score > initial_score
        assert updated_profile.score == initial_score + DOCUMENT_WEIGHTS[DocumentType.BANK_STATEMENT]
        
        # Check event was created
        event = db.query(CreditScoreEvent).filter(
            CreditScoreEvent.user_id == test_customer.id,
            CreditScoreEvent.event_type == "DOCUMENT_APPROVED"
        ).first()
        assert event is not None
        assert event.delta == DOCUMENT_WEIGHTS[DocumentType.BANK_STATEMENT]

    def test_document_rejection_no_score_change(self, db: Session, test_customer):
        """Test that rejecting a document doesn't change score."""
        profile = get_or_create_credit_profile(db, test_customer.id)
        initial_score = profile.score
        
        # Create and reject a document
        document = CreditDocument(
            user_id=test_customer.id,
            document_type=DocumentType.BANK_STATEMENT,
            file_path="/test/path.pdf",
            status=DocumentStatus.PENDING,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Reject it (should not call handle_document_approved)
        document.status = DocumentStatus.REJECTED
        db.commit()
        db.refresh(profile)
        
        # Score should not change
        assert profile.score == initial_score


class TestPaymentScoring:
    """Tests for payment-based scoring."""

    def test_on_time_payment_increases_score(self, db: Session, test_customer):
        """Test that on-time payments increase score."""
        profile = get_or_create_credit_profile(db, test_customer.id)
        initial_score = profile.score
        
        # Create a loan and installment
        loan = Loan(
            customer_id=test_customer.id,
            lender_id=1,  # Assuming lender exists
            product_id=1,  # Assuming product exists
            principal_amount=Decimal("100000"),
            deposit_amount=Decimal("20000"),
            total_amount=Decimal("120000"),
            status=LoanStatus.ACTIVE,
        )
        db.add(loan)
        db.flush()
        
        installment = Installment(
            loan_id=loan.id,
            due_date=datetime.utcnow() + timedelta(days=30),
            amount=Decimal("40000"),
            paid=False,
        )
        db.add(installment)
        db.commit()
        db.refresh(installment)
        
        # Mark as paid on time
        installment.paid = True
        installment.paid_at = datetime.utcnow()  # Before due date
        updated_profile = handle_installment_payment(db, installment)
        
        # Score should increase
        assert updated_profile.score > initial_score

    def test_late_payment_decreases_score(self, db: Session, test_customer):
        """Test that late payments decrease score."""
        profile = get_or_create_credit_profile(db, test_customer.id)
        initial_score = profile.score
        
        # Create a loan and installment
        loan = Loan(
            customer_id=test_customer.id,
            lender_id=1,
            product_id=1,
            principal_amount=Decimal("100000"),
            deposit_amount=Decimal("20000"),
            total_amount=Decimal("120000"),
            status=LoanStatus.ACTIVE,
        )
        db.add(loan)
        db.flush()
        
        due_date = datetime.utcnow() - timedelta(days=10)  # 10 days ago
        installment = Installment(
            loan_id=loan.id,
            due_date=due_date,
            amount=Decimal("40000"),
            paid=False,
        )
        db.add(installment)
        db.commit()
        db.refresh(installment)
        
        # Mark as paid late
        installment.paid = True
        installment.paid_at = datetime.utcnow()  # After due date
        updated_profile = handle_installment_payment(db, installment)
        
        # Score should decrease
        assert updated_profile.score < initial_score


class TestLoanStatusScoring:
    """Tests for loan status change scoring."""

    def test_early_loan_repayment_bonus(self, db: Session, test_customer):
        """Test that early loan repayment gives bonus."""
        profile = get_or_create_credit_profile(db, test_customer.id)
        initial_score = profile.score
        
        # Create a loan
        loan = Loan(
            customer_id=test_customer.id,
            lender_id=1,
            product_id=1,
            principal_amount=Decimal("100000"),
            deposit_amount=Decimal("20000"),
            total_amount=Decimal("120000"),
            status=LoanStatus.ACTIVE,
        )
        db.add(loan)
        db.flush()
        
        # Create installments and mark all as paid early
        for i in range(3):
            installment = Installment(
                loan_id=loan.id,
                due_date=datetime.utcnow() + timedelta(days=30 * (i + 1)),
                amount=Decimal("40000"),
                paid=True,
                paid_at=datetime.utcnow(),  # All paid early
            )
            db.add(installment)
        db.commit()
        db.refresh(loan)
        
        # Change loan status to PAID
        updated_profile = handle_loan_status_change(db, loan, LoanStatus.ACTIVE, LoanStatus.PAID)
        
        if updated_profile:
            assert updated_profile.score > initial_score


class TestRecalculation:
    """Tests for full score recalculation."""

    def test_recalculate_full_score(self, db: Session, test_customer):
        """Test full score recalculation."""
        profile = get_or_create_credit_profile(db, test_customer.id)
        
        # Add some documents
        doc1 = CreditDocument(
            user_id=test_customer.id,
            document_type=DocumentType.BANK_STATEMENT,
            file_path="/test/path1.pdf",
            status=DocumentStatus.APPROVED,
        )
        db.add(doc1)
        db.commit()
        
        # Recalculate
        updated_profile = recalculate_full_score(db, test_customer.id)
        
        assert updated_profile is not None
        assert updated_profile.last_recalculated_at is not None
        assert updated_profile.score >= INITIAL_SCORE  # Should have increased due to document


class TestTierCalculation:
    """Tests for tier and limit calculation."""

    def test_tier_calculation(self):
        """Test tier calculation from score."""
        assert compute_tier_from_score(150) == "TIER_0"
        assert compute_tier_from_score(300) == "TIER_1"
        assert compute_tier_from_score(500) == "TIER_2"
        assert compute_tier_from_score(700) == "TIER_3"
        assert compute_tier_from_score(900) == "TIER_4"

    def test_limit_calculation(self):
        """Test limit calculation from tier."""
        assert compute_limit_from_tier("TIER_0") == Decimal("0")
        assert compute_limit_from_tier("TIER_1") == Decimal("200000.00")
        assert compute_limit_from_tier("TIER_2") == Decimal("800000.00")
        assert compute_limit_from_tier("TIER_3") == Decimal("2000000.00")
        assert compute_limit_from_tier("TIER_4") == Decimal("5000000.00")


class TestCreditAPI:
    """Tests for credit API endpoints."""

    def test_get_credit_profile_endpoint(self, auth_token_customer):
        """Test GET /credit/profile/me endpoint."""
        response = client.get(
            "/credit/profile/me",
            headers={"Authorization": f"Bearer {auth_token_customer}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "tier" in data
        assert "max_bnpl_limit" in data
        assert data["score"] == INITIAL_SCORE

    def test_get_credit_events_endpoint(self, auth_token_customer):
        """Test GET /credit/events/me endpoint."""
        response = client.get(
            "/credit/events/me",
            headers={"Authorization": f"Bearer {auth_token_customer}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data
        assert isinstance(data["events"], list)

    def test_get_documents_endpoint(self, auth_token_customer):
        """Test GET /credit/documents/me endpoint."""
        response = client.get(
            "/credit/documents/me",
            headers={"Authorization": f"Bearer {auth_token_customer}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data

    def test_get_document_status_endpoint(self, auth_token_customer):
        """Test GET /credit/documents/status endpoint."""
        response = client.get(
            "/credit/documents/status",
            headers={"Authorization": f"Bearer {auth_token_customer}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert isinstance(data["documents"], list)
        assert len(data["documents"]) > 0  # Should have all document types

