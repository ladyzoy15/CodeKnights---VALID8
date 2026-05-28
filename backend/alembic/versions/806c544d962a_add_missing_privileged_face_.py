"""Add missing privileged_face_verification_enabled column

Revision ID: 806c544d962a
Revises: 0005_excuse_letters
Create Date: 2026-05-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '806c544d962a'
down_revision: Union[str, None] = '0005_excuse_letters'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if column already exists before adding
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('school_event_policies')]
    
    if 'privileged_face_verification_enabled' not in columns:
        # Use server_default='false' to prevent NotNullViolation on existing rows
        op.add_column('school_event_policies', sa.Column('privileged_face_verification_enabled', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('school_event_policies')]
    
    if 'privileged_face_verification_enabled' in columns:
        op.drop_column('school_event_policies', 'privileged_face_verification_enabled')
