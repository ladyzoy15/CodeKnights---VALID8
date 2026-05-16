"""fix missing tables for login

Revision ID: f3a5e1234567
Revises: e79235331d71
Create Date: 2026-05-12 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f3a5e1234567'
down_revision = 'e79235331d71'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. school_settings
    op.create_table(
        'school_settings',
        sa.Column('school_id', sa.BigInteger(), sa.ForeignKey('schools.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('primary_color', sa.String(length=7), nullable=False, server_default='#162F65'),
        sa.Column('secondary_color', sa.String(length=7), nullable=False, server_default='#2C5F9E'),
        sa.Column('accent_color', sa.String(length=7), nullable=False, server_default='#4A90E2'),
        sa.Column('event_default_early_check_in_minutes', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('event_default_late_threshold_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('event_default_sign_out_grace_minutes', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_by_user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
    )

    # 2. user_face_profiles
    op.create_table(
        'user_face_profiles',
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('face_encoding', sa.LargeBinary(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='arcface'),
        sa.Column('reference_image_sha256', sa.String(length=64), nullable=True),
        sa.Column('last_verified_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # 3. Add face columns to student_profiles
    op.add_column('student_profiles', sa.Column('face_encoding', sa.LargeBinary(), nullable=True))
    op.add_column('student_profiles', sa.Column('embedding_provider', sa.String(length=32), nullable=True))
    op.add_column('student_profiles', sa.Column('embedding_dtype', sa.String(length=16), nullable=True))
    op.add_column('student_profiles', sa.Column('embedding_dimension', sa.Integer(), nullable=True))
    op.add_column('student_profiles', sa.Column('embedding_normalized', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('student_profiles', sa.Column('is_face_registered', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('student_profiles', sa.Column('face_image_url', sa.String(length=500), nullable=True))
    op.add_column('student_profiles', sa.Column('registration_complete', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('student_profiles', sa.Column('last_face_update', sa.DateTime(), nullable=True))

    # 4. Add legacy columns to schools
    op.add_column('schools', sa.Column('logo_url', sa.String(length=1000), nullable=True))
    op.add_column('schools', sa.Column('primary_color', sa.String(length=7), nullable=False, server_default='#162F65'))
    op.add_column('schools', sa.Column('secondary_color', sa.String(length=7), nullable=True))
    op.add_column('schools', sa.Column('subscription_status', sa.String(length=30), nullable=False, server_default='trial'))


def downgrade() -> None:
    op.drop_column('schools', 'subscription_status')
    op.drop_column('schools', 'secondary_color')
    op.drop_column('schools', 'primary_color')
    op.drop_column('schools', 'logo_url')
    op.drop_column('student_profiles', 'last_face_update')
    op.drop_column('student_profiles', 'registration_complete')
    op.drop_column('student_profiles', 'face_image_url')
    op.drop_column('student_profiles', 'is_face_registered')
    op.drop_column('student_profiles', 'embedding_normalized')
    op.drop_column('student_profiles', 'embedding_dimension')
    op.drop_column('student_profiles', 'embedding_dtype')
    op.drop_column('student_profiles', 'embedding_provider')
    op.drop_column('student_profiles', 'face_encoding')
    op.drop_table('user_face_profiles')
    op.drop_table('school_settings')
