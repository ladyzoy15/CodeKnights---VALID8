"""Add attendance_face_recognition_enabled and first_time_face_registration_required

Revision ID: e7ac69b18cd1
Revises: 806c544d962a
Create Date: 2026-05-27 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7ac69b18cd1'
down_revision: Union[str, None] = '806c544d962a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('school_event_policies', sa.Column('attendance_face_recognition_enabled', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('school_event_policies', sa.Column('first_time_face_registration_required', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    op.drop_column('school_event_policies', 'first_time_face_registration_required')
    op.drop_column('school_event_policies', 'attendance_face_recognition_enabled')
