"""add_excuse_letters

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-26 11:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'excuse_letters',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('student_profile_id', sa.BigInteger(), nullable=False),
        sa.Column('event_id', sa.BigInteger(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('attachment_url', sa.Text(), nullable=True),
        sa.Column('status', sa.Text(), nullable=False, server_default='Pending'),
        sa.Column('reviewer_id', sa.BigInteger(), nullable=True),
        sa.Column('reviewer_remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['student_profile_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_excuse_letters_event_id'), 'excuse_letters', ['event_id'], unique=False)
    op.create_index(op.f('ix_excuse_letters_student_profile_id'), 'excuse_letters', ['student_profile_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_excuse_letters_student_profile_id'), table_name='excuse_letters')
    op.drop_index(op.f('ix_excuse_letters_event_id'), table_name='excuse_letters')
    op.drop_table('excuse_letters')
