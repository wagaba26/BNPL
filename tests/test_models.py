import pytest
from decimal import Decimal
from app.models.user import User, UserRole
from app.models.retailer import Retailer
from app.models.mfi import MFI
from app.models.product import Product
from app.models.loan import Loan, LoanStatus
from app.services.auth import get_password_hash


def test_user_model(db):
    """Test User model creation."""
    user = User(
        email="model@test.com",
        phone="1111111111",
        hashed_password=get_password_hash("password"),
        full_name="Model Test",
        role=UserRole.CUSTOMER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.email == "model@test.com"
    assert user.role == UserRole.CUSTOMER


def test_retailer_model(db, test_user):
    """Test Retailer model creation."""
    retailer = Retailer(
        user_id=test_user.id,
        business_name="Test Business",
        registration_number="REG123",
    )
    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    assert retailer.id is not None
    assert retailer.business_name == "Test Business"
    assert retailer.user_id == test_user.id


def test_mfi_model(db):
    """Test MFI model creation."""
    user = User(
        email="mfi@test.com",
        phone="2222222222",
        hashed_password=get_password_hash("password"),
        full_name="MFI Test",
        role=UserRole.LENDER,
    )
    db.add(user)
    db.commit()

    mfi = MFI(
        user_id=user.id,
        institution_name="Test MFI",
        interest_rate=Decimal("12.5"),
        min_credit_score=600,
    )
    db.add(mfi)
    db.commit()
    db.refresh(mfi)

    assert mfi.id is not None
    assert mfi.institution_name == "Test MFI"
    assert mfi.interest_rate == Decimal("12.5")


def test_product_model(db, test_retailer_user):
    """Test Product model creation."""
    from app.models.retailer import Retailer

    retailer = db.query(Retailer).filter(Retailer.user_id == test_retailer_user.id).first()

    product = Product(
        retailer_id=retailer.id,
        name="Test Product",
        price=Decimal("1000.00"),
        deposit_percentage=Decimal("10.00"),
        is_bnpl_eligible=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    assert product.id is not None
    assert product.name == "Test Product"
    assert product.price == Decimal("1000.00")
    assert product.is_bnpl_eligible is True

