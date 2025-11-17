"""
Standalone script to seed development accounts.

Run this script directly to create the development accounts:
    python seed_dev_accounts.py
"""

import sys
import os

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.seed import seed_dev_accounts

if __name__ == "__main__":
    print("=" * 60)
    print("Seeding Development Accounts")
    print("=" * 60)
    try:
        seed_dev_accounts()
        print("\n[SUCCESS] Development accounts seeded successfully!")
        print("\nYou can now login with:")
        print("  - CUSTOMER: wagabac / admin")
        print("  - RETAILER: wagabar / admin")
        print("  - LENDER: wagabal / admin")
    except Exception as e:
        print(f"\n[ERROR] Error seeding accounts: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

