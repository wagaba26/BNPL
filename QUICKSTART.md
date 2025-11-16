# Quick Start Guide

This guide will help you get the BNPL platform running locally in minutes.

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+

## Step 1: Start PostgreSQL

```bash
docker-compose up -d
```

This starts PostgreSQL on port 5432.

## Step 2: Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy this content:
# DATABASE_URL=postgresql://bnpl_user:bnpl_password@localhost:5432/bnpl_db
# SECRET_KEY=your-secret-key-change-in-production
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30

# Run migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

Backend will be at: http://localhost:8000
API Docs: http://localhost:8000/docs

## Step 3: Set Up Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Start dev server
npm run dev
```

Frontend will be at: http://localhost:3000

## Step 4: Test the Platform

1. **Register a Customer:**
   - Go to http://localhost:3000/register
   - Create an account (defaults to CUSTOMER role)
   - You'll be automatically logged in

2. **View Dashboard:**
   - You'll see your credit profile (default: score 300, limit 200,000)

3. **Create a Retailer Account (via API):**
   ```bash
   # Register as retailer (you'll need to manually update role in DB or add an endpoint)
   # For now, you can test with the API directly
   ```

4. **Create a Product (as Retailer):**
   - Login as retailer
   - Go to /retailer/products
   - Add a new product

5. **Request BNPL (as Customer):**
   - Browse marketplace at /customer/marketplace
   - Click "Buy Now, Pay Later" on a product
   - Confirm the BNPL request

## Testing API Endpoints

You can test the API using the Swagger UI at http://localhost:8000/docs

Example: Register a user
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "test123"
  }'
```

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `docker-compose ps`
- Check .env file exists and has correct DATABASE_URL
- Make sure migrations ran: `alembic upgrade head`

### Frontend can't connect to backend
- Check NEXT_PUBLIC_API_BASE_URL in .env.local
- Make sure backend is running on port 8000
- Check browser console for CORS errors

### Database connection errors
- Ensure PostgreSQL container is running: `docker-compose up -d`
- Check DATABASE_URL in backend/.env matches docker-compose.yml

## Next Steps

- Read the full README.md for detailed documentation
- Check backend/README.md for backend-specific details
- Check frontend/README.md for frontend-specific details

