# BNPL Platform - Backend

FastAPI backend for the Buy Now Pay Later (BNPL) platform.

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Alembic (migrations)
- PostgreSQL
- JWT authentication (python-jose)
- Password hashing (passlib/bcrypt)

## Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+ (or use Docker Compose)
- pip

### Installation

1. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

   On Windows:
   ```powershell
   venv\Scripts\activate
   ```

   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**

   Create a `.env` file in the `backend` directory:

   ```env
   DATABASE_URL=postgresql://bnpl_user:bnpl_password@localhost:5432/bnpl_db
   SECRET_KEY=your-secret-key-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Set up PostgreSQL database:**

   ```bash
   # Create database
   createdb bnpl_db
   
   # Or using psql:
   psql -U postgres
   CREATE DATABASE bnpl_db;
   CREATE USER bnpl_user WITH PASSWORD 'bnpl_password';
   GRANT ALL PRIVILEGES ON DATABASE bnpl_db TO bnpl_user;
   ```

5. **Run migrations:**

   ```bash
   alembic upgrade head
   ```

   If this is the first time, create an initial migration:

   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

6. **Run the application:**

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The API will be available at:
   - API: http://localhost:8000
   - API Documentation (Swagger): http://localhost:8000/docs
   - API Documentation (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user (defaults to CUSTOMER)
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user info

### Credit Profile

- `GET /credit-profile/me` - Get current user's credit profile (CUSTOMER only)

### Products

- `GET /products` - Get products available for BNPL (CUSTOMER only, filtered by credit profile)
- `GET /products/retailer/products` - List retailer's products (RETAILER only)
- `POST /products/retailer/products` - Create new product (RETAILER only)
- `PUT /products/retailer/products/{id}` - Update product (RETAILER only)
- `DELETE /products/retailer/products/{id}` - Delete product (RETAILER only)

### Loans / BNPL

- `POST /loans/bnpl-requests` - Create a BNPL request (CUSTOMER only)
- `GET /loans/me` - Get current customer's loans
- `GET /loans/lender/loans` - Get loans for current lender (LENDER only)

## Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback migration:

```bash
alembic downgrade -1
```

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app
```

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py         # Database connection
│   │   ├── dependencies.py     # Auth dependencies
│   │   └── security.py         # Password hashing, JWT
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── retailer.py
│   │   ├── lender.py
│   │   ├── credit_profile.py
│   │   ├── product.py
│   │   ├── loan.py
│   │   └── installment.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── credit_profile.py
│   │   ├── product.py
│   │   └── loan.py
│   ├── routers/                # API routers
│   │   ├── auth.py
│   │   ├── credit_profile.py
│   │   ├── products.py
│   │   └── loans.py
│   └── main.py                 # FastAPI application
├── alembic/                    # Database migrations
├── requirements.txt
├── alembic.ini
└── README.md
```

