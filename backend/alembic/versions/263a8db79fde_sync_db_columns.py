"""sync_db_columns — add face_encoding and related columns to student_profiles

Revision ID: 263a8db79fde
Revises: e7ac69b18cd1
Create Date: 2026-05-27 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '263a8db79fde'
down_revision: Union[str, None] = 'e7ac69b18cd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # These columns were added to sync the student_profiles table with the
    # updated StudentProfile model that includes face recognition fields.
    # Using try/except per-column so the migration is idempotent (safe to run
    # even if columns already exist).
    conn = op.get_bind()

    columns = [
        ("face_encoding", "BYTEA"),
        ("embedding_provider", "VARCHAR"),
        ("embedding_dtype", "VARCHAR"),
        ("embedding_dimension", "INTEGER"),
        ("embedding_normalized", "BOOLEAN"),
        ("is_face_registered", "BOOLEAN DEFAULT FALSE"),
        ("face_image_url", "VARCHAR"),
        ("registration_complete", "BOOLEAN DEFAULT FALSE"),
        ("last_face_update", "TIMESTAMP WITH TIME ZONE"),
    ]

    for col_name, col_type in columns:
        exists = conn.execute(
            sa.text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name='student_profiles' AND column_name=:col"
            ),
            {"col": col_name},
        ).fetchone()
        if not exists:
            conn.execute(sa.text(
                f"ALTER TABLE student_profiles ADD COLUMN {col_name} {col_type}"
            ))


def downgrade() -> None:
    cols = [
        "face_encoding", "embedding_provider", "embedding_dtype",
        "embedding_dimension", "embedding_normalized", "is_face_registered",
        "face_image_url", "registration_complete", "last_face_update",
    ]
    for col in cols:
        conn = op.get_bind()
        conn.execute(sa.text(
            f"ALTER TABLE student_profiles DROP COLUMN IF EXISTS {col}"
        ))
