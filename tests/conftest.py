import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.services.auth import get_password_hash
from app.models.user import User, UserRole
from app.models.retailer import Retailer
from app.models.mfi import MFI
from app.models.product import Product

# Test database URL (using SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with dependency overrides."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        phone="1234567890",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        role=UserRole.CUSTOMER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_retailer_user(db):
    """Create a test retailer user."""
    user = User(
        email="retailer@example.com",
        phone="1234567891",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test Retailer",
        role=UserRole.RETAILER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    retailer = Retailer(
        user_id=user.id,
        business_name="Test Retailer Business",
    )
    db.add(retailer)
    db.commit()
    db.refresh(retailer)
    return user


@pytest.fixture
def test_lender_user(db):
    """Create a test lender user."""
    user = User(
        email="lender@example.com",
        phone="1234567892",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test Lender",
        role=UserRole.LENDER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    mfi = MFI(
        user_id=user.id,
        institution_name="Test MFI",
        interest_rate=10.0,
        min_credit_score=500,
    )
    db.add(mfi)
    db.commit()
    db.refresh(mfi)
    return user

