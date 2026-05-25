"""Add excuse_letters table and review_excuse_letter permission

Revision ID: 0005_excuse_letters
Revises: b033a6f7e275
Create Date: 2026-05-24 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_excuse_letters"
down_revision = "b033a6f7e275"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "excuse_letters",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("school_id", sa.BigInteger(), sa.ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("event_id", sa.BigInteger(), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("student_profile_id", sa.BigInteger(), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("attachment_path", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending", index=True),
        sa.Column("reviewed_by_user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("reviewer_remarks", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("event_id", "student_profile_id", name="excuse_letters_event_id_student_profile_id_key"),
    )

    # Seed the new permission into governance_permissions if it doesn't exist yet
    op.execute("""
        INSERT INTO governance_permissions (permission_code, permission_name, description)
        VALUES (
            'review_excuse_letter',
            'Review Excuse Letter',
            'Allows members of the unit to review, approve, or reject excuse letters submitted by students for events within their governance scope.'
        )
        ON CONFLICT (permission_code) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM governance_permissions WHERE permission_code = 'review_excuse_letter'
    """)
    op.drop_table("excuse_letters")
