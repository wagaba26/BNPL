# Troubleshooting Guide

## Login and Registration Issues

If you're experiencing issues with login or registration, follow these steps:

### 1. Check Backend Server Status

The frontend requires the backend API to be running. Make sure:

- **Backend is running**: Navigate to `backend/` directory and start the server:
  ```bash
  cd backend
  uvicorn app.main:app --reload --port 8000
  ```
  
  Or use the provided scripts:
  - Windows: `start_server.bat` or `start_server.ps1`
  - Linux/Mac: `python -m uvicorn app.main:app --reload --port 8000`

- **Backend is accessible**: Open http://localhost:8000/docs in your browser to verify the API is running

### 2. Check Frontend Environment Variables

The frontend needs to know where the backend API is located:

1. Create a `.env.local` file in the `frontend/` directory (if it doesn't exist)
2. Add the following line:
   ```
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```
3. Restart the Next.js dev server after creating/modifying `.env.local`

### 3. Verify Database Setup

The backend requires a database. By default, it uses SQLite (`bnpl_dev.db`):

- **SQLite (Default)**: No setup required - the database file is created automatically
- **PostgreSQL**: If using PostgreSQL, ensure:
  - PostgreSQL is running
  - Database is created
  - `DATABASE_URL` is set in `backend/.env`

### 4. Common Error Messages

#### "Cannot connect to backend server"
- **Cause**: Backend is not running or API URL is incorrect
- **Solution**: 
  1. Start the backend server (see step 1)
  2. Verify `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local`
  3. Check that the backend is accessible at the configured URL

#### "Invalid email/username or password"
- **Cause**: Wrong credentials or user doesn't exist
- **Solution**: 
  1. Verify your credentials
  2. Try registering a new account
  3. Check backend logs for more details

#### "Email already registered"
- **Cause**: An account with that email already exists
- **Solution**: Use a different email or try logging in instead

#### "Trading license is required for retailer registration"
- **Cause**: Retailer registration requires a trading license number
- **Solution**: Provide a valid trading license number when registering as a retailer

#### "Admin code is required for lender registration"
- **Cause**: Lender registration requires an admin code for due diligence
- **Solution**: Contact support to obtain the admin code (default: `LENDER2024` for development)

### 5. Development Account Setup

For testing, you can seed development accounts:

1. Navigate to `backend/` directory
2. Run the seed script:
   ```bash
   python seed_dev_accounts.py
   ```

Default dev accounts:
- **Customer**: email: `customer@example.com`, password: `admin`
- **Retailer**: email: `wagabar`, password: `admin`
- **Lender**: email: `lender@example.com`, password: `admin`

### 6. Network Issues

If you're still experiencing connection issues:

1. **Check firewall**: Ensure port 8000 (backend) and 3000 (frontend) are not blocked
2. **Check CORS**: The backend should allow requests from `http://localhost:3000`
3. **Check browser console**: Open browser DevTools (F12) and check the Console and Network tabs for errors

### 7. Database Migration Issues

If you see database-related errors:

1. Run migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

2. If tables don't exist, create them:
   ```bash
   python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

### 8. Still Having Issues?

1. Check backend logs for detailed error messages
2. Check browser console (F12) for frontend errors
3. Verify all environment variables are set correctly
4. Ensure all dependencies are installed:
   - Backend: `pip install -r requirements.txt`
   - Frontend: `npm install`

## Registration Requirements by Role

### Customer
- Email (required)
- Full Name (required)
- Password (required, min 6 characters)
- Phone (optional)

### Retailer
- All customer requirements, plus:
- **Trading License Number** (required) - Part of due diligence verification
- Business Name (required)

### Lender
- All customer requirements, plus:
- **Admin Code** (required) - Contact support to obtain
- Institution Name (required)

