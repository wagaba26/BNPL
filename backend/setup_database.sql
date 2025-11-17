-- BNPL Database Setup Script
-- Run this script as the PostgreSQL superuser (usually 'postgres')

-- Create the database
CREATE DATABASE bnpl_db;

-- Create the user
CREATE USER bnpl_user WITH PASSWORD 'bnpl_password';

-- Grant privileges on the database
GRANT ALL PRIVILEGES ON DATABASE bnpl_db TO bnpl_user;

-- Connect to the new database (this is a psql command, not SQL)
-- In psql, run: \c bnpl_db
-- Then run the commands below:

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO bnpl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO bnpl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO bnpl_user;

