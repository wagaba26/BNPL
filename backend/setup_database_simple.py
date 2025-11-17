"""
Simple database setup script.

Tries to set up the database using common default configurations.
If it fails, it will provide instructions for manual setup.
"""

import sys
import os

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def setup_database():
    """Set up the database and user."""
    
    print("=" * 60)
    print("BNPL Database Setup")
    print("=" * 60)
    print()
    
    # Common connection attempts
    attempts = [
        ("postgres", ""),  # No password (trust authentication)
        ("postgres", "postgres"),  # Common default password
        ("postgres", "admin"),  # Another common default
    ]
    
    engine = None
    postgres_user = None
    
    for user, password in attempts:
        conn_str = f"postgresql://{user}:{password}@localhost:5432/postgres" if password else f"postgresql://{user}@localhost:5432/postgres"
        try:
            print(f"Trying to connect as '{user}'...")
            engine = create_engine(conn_str, isolation_level="AUTOCOMMIT")
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"✓ Connected as '{user}'!")
            postgres_user = user
            break
        except Exception as e:
            print(f"✗ Failed: {str(e)[:80]}")
            continue
    
    if engine is None:
        print("\n" + "=" * 60)
        print("Could not connect automatically.")
        print("=" * 60)
        print("\nPlease set up the database manually:")
        print("\nOption 1: Using psql command line:")
        print("  psql -U postgres")
        print("  CREATE DATABASE bnpl_db;")
        print("  CREATE USER bnpl_user WITH PASSWORD 'bnpl_password';")
        print("  GRANT ALL PRIVILEGES ON DATABASE bnpl_db TO bnpl_user;")
        print("  \\c bnpl_db")
        print("  GRANT ALL ON SCHEMA public TO bnpl_user;")
        print("  \\q")
        print("\nOption 2: Using pgAdmin or another PostgreSQL GUI tool")
        print("\nOption 3: If you have different credentials, update backend/.env with:")
        print("  DATABASE_URL=postgresql://your_user:your_password@localhost:5432/your_database")
        return False
    
    try:
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = 'bnpl_db'"
            ))
            db_exists = result.fetchone() is not None
            
            if db_exists:
                print("\n✓ Database 'bnpl_db' already exists")
            else:
                print("\nCreating database 'bnpl_db'...")
                conn.execute(text('CREATE DATABASE bnpl_db'))
                print("✓ Database created successfully!")
            
            # Check if user exists
            result = conn.execute(text(
                "SELECT 1 FROM pg_user WHERE usename = 'bnpl_user'"
            ))
            user_exists = result.fetchone() is not None
            
            if user_exists:
                print("✓ User 'bnpl_user' already exists")
                # Update password
                print("Updating user password...")
                conn.execute(text("ALTER USER bnpl_user WITH PASSWORD 'bnpl_password'"))
                print("✓ Password updated!")
            else:
                print("Creating user 'bnpl_user'...")
                conn.execute(text(
                    "CREATE USER bnpl_user WITH PASSWORD 'bnpl_password'"
                ))
                print("✓ User created successfully!")
            
            # Grant privileges
            print("Granting privileges...")
            conn.execute(text("GRANT ALL PRIVILEGES ON DATABASE bnpl_db TO bnpl_user"))
            print("✓ Privileges granted!")
            
            # Connect to bnpl_db to grant schema privileges
            conn_str_bnpl = f"postgresql://{postgres_user}@localhost:5432/bnpl_db" if not attempts[0][1] else f"postgresql://{postgres_user}:{attempts[0][1]}@localhost:5432/bnpl_db"
            bnpl_engine = create_engine(conn_str_bnpl, isolation_level="AUTOCOMMIT")
            with bnpl_engine.connect() as bnpl_conn:
                bnpl_conn.execute(text("GRANT ALL ON SCHEMA public TO bnpl_user"))
                bnpl_conn.execute(text("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO bnpl_user"))
                bnpl_conn.execute(text("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO bnpl_user"))
            print("✓ Schema privileges granted!")
            
        print("\n" + "=" * 60)
        print("[SUCCESS] Database setup completed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease set up the database manually using the instructions above.")
        return False

if __name__ == "__main__":
    success = setup_database()
    if success:
        print("\nNext steps:")
        print("1. Run migrations: cd backend && alembic upgrade head")
        print("2. Seed accounts: python seed_dev_accounts.py")
    sys.exit(0 if success else 1)

