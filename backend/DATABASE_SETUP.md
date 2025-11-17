# Database Setup Guide

This guide will help you set up the PostgreSQL database for the BNPL platform.

## Quick Setup (Using SQL Script)

1. **Connect to PostgreSQL** using one of these methods:

   **Option A: Using psql command line**
   ```powershell
   # If psql is in your PATH:
   psql -U postgres
   
   # Or if you need to specify the full path:
   # (Find your PostgreSQL installation, typically in Program Files)
   "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
   ```

   **Option B: Using pgAdmin** (GUI tool)
   - Open pgAdmin
   - Connect to your PostgreSQL server
   - Open Query Tool
   - Paste and run the SQL commands below

   **Option C: Using any PostgreSQL client**
   - Connect as the superuser (usually `postgres`)
   - Run the SQL commands below

2. **Run this SQL script:**

```sql
-- Create the database
CREATE DATABASE bnpl_db;

-- Create the user
CREATE USER bnpl_user WITH PASSWORD 'bnpl_password';

-- Grant privileges on the database
GRANT ALL PRIVILEGES ON DATABASE bnpl_db TO bnpl_user;

-- Connect to the new database
\c bnpl_db

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO bnpl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO bnpl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO bnpl_user;
```

3. **Create the .env file** in the `backend` directory:

Create a file named `.env` with this content:
```
DATABASE_URL=postgresql://bnpl_user:bnpl_password@localhost:5432/bnpl_db
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEV_SEED=true
DEBUG=True
APP_NAME=BNPL Platform
```

4. **Run database migrations:**
   ```powershell
   cd backend
   alembic upgrade head
   ```

5. **Seed development accounts:**
   ```powershell
   python seed_dev_accounts.py
   ```

## Alternative: Using Docker

If you have Docker installed:

```powershell
# Start PostgreSQL container
docker-compose up -d

# Wait a few seconds for PostgreSQL to start, then run migrations
cd backend
alembic upgrade head

# Seed accounts
python seed_dev_accounts.py
```

## Troubleshooting

### "password authentication failed"
- Make sure you're using the correct PostgreSQL superuser password
- Check your `pg_hba.conf` file if you're having authentication issues

### "database does not exist"
- Make sure you ran the `CREATE DATABASE` command
- Verify the database name matches in your `.env` file

### "permission denied"
- Make sure you granted all the necessary privileges to `bnpl_user`
- Try re-running the GRANT commands

### Can't find psql
- PostgreSQL might not be in your PATH
- Look for it in: `C:\Program Files\PostgreSQL\[version]\bin\`
- Or use pgAdmin GUI instead

## After Setup

Once the database is set up, you can:

1. **Start the FastAPI server:**
   ```powershell
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **Login with development accounts:**
   - CUSTOMER: `wagabac` / `admin`
   - RETAILER: `wagabar` / `admin`
   - LENDER: `wagabal` / `admin`

