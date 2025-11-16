import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.core.security import get_password_hash

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
        db.close()


def test_register_user():
    """Test user registration."""
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["role"] == "CUSTOMER"


def test_register_duplicate_email():
    """Test registration with duplicate email."""
    # Register first user
    client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "duplicate@example.com",
            "password": "testpassword123",
        },
    )
    
    # Try to register again with same email
    response = client.post(
        "/auth/register",
        json={
            "name": "Another User",
            "email": "duplicate@example.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 400


def test_login_success():
    """Test successful login."""
    # First register a user
    client.post(
        "/auth/register",
        json={
            "name": "Login Test",
            "email": "login@example.com",
            "password": "testpassword123",
        },
    )
    
    # Then login
    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login@example.com"


def test_login_wrong_password():
    """Test login with wrong password."""
    # Register a user
    client.post(
        "/auth/register",
        json={
            "name": "Wrong Pass",
            "email": "wrongpass@example.com",
            "password": "correctpassword",
        },
    )
    
    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


def test_get_me_without_token():
    """Test getting user info without token."""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_get_me_with_token():
    """Test getting user info with valid token."""
    # Register and get token
    register_response = client.post(
        "/auth/register",
        json={
            "name": "Me Test",
            "email": "me@example.com",
            "password": "testpassword123",
        },
    )
    token = register_response.json()["access_token"]
    
    # Get user info
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"

