"""create initial core tables

Revision ID: 0001_initial
Revises: 
Create Date: 2026-03-14 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255)),
        sa.Column('role', sa.String(length=32)),
        sa.Column('password_hash', sa.String(length=255)),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=128), nullable=False, unique=True),
    )

    op.create_table(
        'lectures',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(length=512)),
        sa.Column('description', sa.Text()),
        sa.Column('source_type', sa.String(length=32)),
        sa.Column('source_url', sa.Text()),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('language', sa.String(length=16)),
        sa.Column('duration_seconds', sa.Integer()),
        sa.Column('status', sa.String(length=32)),
        sa.Column('metadata_', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'media_files',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lecture_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lectures.id', ondelete='CASCADE')),
        sa.Column('file_type', sa.String(length=32)),
        sa.Column('storage_path', sa.Text()),
        sa.Column('checksum', sa.String(length=128)),
        sa.Column('size_bytes', sa.Integer()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'processing_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lecture_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lectures.id', ondelete='CASCADE')),
        sa.Column('job_type', sa.String(length=64)),
        sa.Column('status', sa.String(length=32)),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('finished_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('attempts', sa.Integer(), server_default='0'),
        sa.Column('result', postgresql.JSONB()),
        sa.Column('worker_info', postgresql.JSONB()),
    )

    op.create_table(
        'transcripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lecture_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lectures.id', ondelete='CASCADE')),
        sa.Column('content', sa.Text()),
        sa.Column('segments', postgresql.JSONB()),
        sa.Column('model_info', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'frames',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lecture_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lectures.id', ondelete='CASCADE')),
        sa.Column('timestamp_seconds', sa.Float()),
        sa.Column('image_path', sa.Text()),
        sa.Column('ocr_text', sa.Text()),
        sa.Column('features', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'visual_elements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('frame_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('frames.id', ondelete='CASCADE')),
        sa.Column('element_type', sa.String(length=64)),
        sa.Column('bbox', postgresql.JSONB()),
        sa.Column('extracted_text', sa.Text()),
        sa.Column('semantic_description', sa.Text()),
        sa.Column('confidence', sa.Float()),
        sa.Column('extra', postgresql.JSONB()),
    )

    op.create_table(
        'pedagogical_scripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lecture_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lectures.id', ondelete='CASCADE')),
        sa.Column('version', sa.Integer(), server_default='1'),
        sa.Column('content', sa.Text()),
        sa.Column('sections', postgresql.JSONB()),
        sa.Column('generated_by', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'audio_lectures',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lecture_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lectures.id', ondelete='CASCADE')),
        sa.Column('script_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pedagogical_scripts.id', ondelete='SET NULL')),
        sa.Column('tts_voice', sa.String(length=128)),
        sa.Column('audio_path', sa.Text()),
        sa.Column('duration_seconds', sa.Float()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'model_resources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=256)),
        sa.Column('type', sa.String(length=64)),
        sa.Column('version', sa.String(length=64)),
        sa.Column('config', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True)),
        sa.Column('action', sa.String(length=256)),
        sa.Column('details', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'annotations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lecture_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lectures.id', ondelete='CASCADE')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('target_type', sa.String(length=64)),
        sa.Column('target_id', postgresql.UUID(as_uuid=True)),
        sa.Column('note', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'lecture_tags',
        sa.Column('lecture_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lectures.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    )

    # Indexes
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_lectures_uploaded_by'), 'lectures', ['uploaded_by'], unique=False)
    op.create_index(op.f('ix_lectures_status'), 'lectures', ['status'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_lectures_status'), table_name='lectures')
    op.drop_index(op.f('ix_lectures_uploaded_by'), table_name='lectures')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('lecture_tags')
    op.drop_table('annotations')
    op.drop_table('audit_logs')
    op.drop_table('model_resources')
    op.drop_table('audio_lectures')
    op.drop_table('pedagogical_scripts')
    op.drop_table('visual_elements')
    op.drop_table('frames')
    op.drop_table('transcripts')
    op.drop_table('processing_jobs')
    op.drop_table('media_files')
    op.drop_table('lectures')
    op.drop_table('tags')
    op.drop_table('users')
