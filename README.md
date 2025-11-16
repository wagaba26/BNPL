# BNPL (Buy Now Pay Later) Platform

A full-stack BNPL platform connecting Customers, Retailers, and Lenders (MFI/SACCO) for Buy Now Pay Later services.

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Alembic (migrations)
- PostgreSQL
- JWT authentication

### Frontend
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- React Query
- Zustand (state management)

## Project Structure

```
BNPL/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── routers/       # API endpoints
│   │   └── main.py        # FastAPI app
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── frontend/             # Next.js frontend
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities, API client, hooks
│   └── package.json
├── docker-compose.yml    # PostgreSQL service
└── README.md
```

## Quick Start

### Prerequisites

- Docker and Docker Compose (for PostgreSQL)
- Python 3.11+ (for backend)
- Node.js 18+ (for frontend)

### 1. Start PostgreSQL

```bash
docker-compose up -d
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy the example and update values:
# DATABASE_URL=postgresql://bnpl_user:bnpl_password@localhost:5432/bnpl_db
# SECRET_KEY=your-secret-key-change-in-production
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30

# Run migrations
alembic upgrade head

# If first time, create initial migration:
# alembic revision --autogenerate -m "Initial migration"
# alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API Docs: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Features

### User Roles

- **CUSTOMER**: Browse products, request BNPL loans, view loan status
- **RETAILER**: List products, manage inventory
- **LENDER**: View loans, track repayments

### Core Functionality

1. **Authentication**: JWT-based auth with role-based access
2. **Credit Profile**: Default credit score and BNPL limit for customers
3. **Product Management**: Retailers can list BNPL-eligible products
4. **BNPL Requests**: Customers can request loans for products
5. **Loan Management**: Automatic installment schedule generation
6. **Loan Tracking**: View loans by customer or lender

## API Endpoints

### Authentication
- `POST /auth/register` - Register as CUSTOMER
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user

### Credit Profile
- `GET /credit-profile/me` - Get customer credit profile

### Products
- `GET /products` - Get available products (CUSTOMER)
- `GET /products/retailer/products` - List retailer's products
- `POST /products/retailer/products` - Create product
- `PUT /products/retailer/products/{id}` - Update product
- `DELETE /products/retailer/products/{id}` - Delete product

### Loans
- `POST /loans/bnpl-requests` - Create BNPL request
- `GET /loans/me` - Get customer's loans
- `GET /loans/lender/loans` - Get lender's loans

## Frontend Pages

### Public
- `/login` - Login page
- `/register` - Registration page

### Customer Area (`/customer`)
- `/customer/dashboard` - Credit profile and loan summary
- `/customer/marketplace` - Browse BNPL products
- `/customer/checkout/[productId]` - BNPL checkout
- `/customer/loans` - View all loans
- `/customer/profile` - User profile

### Retailer Area (`/retailer`)
- `/retailer/dashboard` - Retailer overview
- `/retailer/products` - Manage products

### Lender Area (`/lender`)
- `/lender/dashboard` - Lender overview
- `/lender/loans` - View all loans

## Development

### Backend

See `backend/README.md` for detailed backend setup instructions.

### Frontend

See `frontend/README.md` for detailed frontend setup instructions.

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://bnpl_user:bnpl_password@localhost:5432/bnpl_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Testing

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm test
```

## Production Deployment

Before deploying:

1. Change `SECRET_KEY` to a strong random value
2. Set proper CORS origins
3. Use production database credentials
4. Configure environment variables
5. Set up SSL/TLS certificates
6. Review security settings

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
