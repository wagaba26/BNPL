"""add_trading_license_to_retailers

Revision ID: 002_add_trading_license
Revises: 001_add_credit_scoring
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_trading_license'
down_revision = '001_add_credit_scoring'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add trading_license column to retailers table
    op.add_column('retailers', sa.Column('trading_license', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove trading_license column from retailers table
    op.drop_column('retailers', 'trading_license')

