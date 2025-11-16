import pytest
from decimal import Decimal


def test_get_current_user(client, test_user):
    """Test getting current user info."""
    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email


def test_create_product(client, test_retailer_user):
    """Test creating a product as retailer."""
    # Login as retailer
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_retailer_user.email,
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    # Create product
    response = client.post(
        "/api/v1/merchants/products",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "New Product",
            "price": "500.00",
            "deposit_percentage": "15.00",
            "is_bnpl_eligible": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Product"


def test_list_products(client):
    """Test listing all products."""
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_request_loan(client, test_user, test_retailer_user, db):
    """Test requesting a loan."""
    from app.models.retailer import Retailer
    from app.models.product import Product

    # Get retailer and create a product
    retailer = db.query(Retailer).filter(Retailer.user_id == test_retailer_user.id).first()
    product = Product(
        retailer_id=retailer.id,
        name="Loan Product",
        price=Decimal("1000.00"),
        deposit_percentage=Decimal("10.00"),
        is_bnpl_eligible=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Login as customer
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    # Create lender
    from app.models.mfi import MFI
    from app.models.user import User, UserRole
    from app.services.auth import get_password_hash

    lender_user = User(
        email="lender2@example.com",
        phone="3333333333",
        hashed_password=get_password_hash("password"),
        full_name="Lender 2",
        role=UserRole.LENDER,
    )
    db.add(lender_user)
    db.commit()

    mfi = MFI(
        user_id=lender_user.id,
        institution_name="Test Lender",
        interest_rate=Decimal("10.0"),
        min_credit_score=400,
        is_active=True,
    )
    db.add(mfi)
    db.commit()

    # Request loan
    response = client.post(
        "/api/v1/loans/request",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product.id,
            "number_of_installments": 3,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == product.id
    assert data["status"] == "pending"

