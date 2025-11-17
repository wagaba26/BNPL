"""add_credit_scoring_models

Revision ID: 001_add_credit_scoring
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_credit_scoring'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update credit_profiles table to add last_recalculated_at
    op.add_column('credit_profiles', sa.Column('last_recalculated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create credit_score_events table
    op.create_table(
        'credit_score_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('delta', sa.Integer(), nullable=False),
        sa.Column('score_before', sa.Integer(), nullable=False),
        sa.Column('score_after', sa.Integer(), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_credit_score_events_user_id'), 'credit_score_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_credit_score_events_event_type'), 'credit_score_events', ['event_type'], unique=False)
    op.create_foreign_key('fk_credit_score_events_user_id', 'credit_score_events', 'users', ['user_id'], ['id'])
    
    # Create credit_documents table
    op.create_table(
        'credit_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.Enum('MOBILE_MONEY_STATEMENT', 'BANK_STATEMENT', 'PROOF_OF_ADDRESS', 'PAYSLIP', 'EMPLOYMENT_CONTRACT', 'BUSINESS_REGISTRATION', 'LC1_LETTER', 'OTHER', name='documenttype'), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='documentstatus'), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_credit_documents_user_id'), 'credit_documents', ['user_id'], unique=False)
    op.create_foreign_key('fk_credit_documents_user_id', 'credit_documents', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_credit_documents_reviewer_id', 'credit_documents', 'users', ['reviewer_id'], ['id'])


def downgrade() -> None:
    # Drop credit_documents table
    op.drop_constraint('fk_credit_documents_reviewer_id', 'credit_documents', type_='foreignkey')
    op.drop_constraint('fk_credit_documents_user_id', 'credit_documents', type_='foreignkey')
    op.drop_index(op.f('ix_credit_documents_user_id'), table_name='credit_documents')
    op.drop_table('credit_documents')
    op.execute('DROP TYPE IF EXISTS documentstatus')
    op.execute('DROP TYPE IF EXISTS documenttype')
    
    # Drop credit_score_events table
    op.drop_constraint('fk_credit_score_events_user_id', 'credit_score_events', type_='foreignkey')
    op.drop_index(op.f('ix_credit_score_events_event_type'), table_name='credit_score_events')
    op.drop_index(op.f('ix_credit_score_events_user_id'), table_name='credit_score_events')
    op.drop_table('credit_score_events')
    
    # Remove last_recalculated_at from credit_profiles
    op.drop_column('credit_profiles', 'last_recalculated_at')

