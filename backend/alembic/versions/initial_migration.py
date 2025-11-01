"""Initial migration

Revision ID: 001
Revises:
Create Date: 2025-10-31 20:11:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create cards table
    op.create_table('cards',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('x', sa.Integer(), nullable=True),
        sa.Column('y', sa.Integer(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('parent_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['cards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create notes table
    op.create_table('notes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('x', sa.Integer(), nullable=True),
        sa.Column('y', sa.Integer(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('card_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create files table
    op.create_table('files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('filepath', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('card_id', sa.String(), nullable=True),
        sa.Column('note_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create task_links table
    op.create_table('task_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.String(), nullable=False),
        sa.Column('target_id', sa.String(), nullable=True),
        sa.Column('link_type', sa.String(), nullable=False),
        sa.Column('link_target_type', sa.String(), server_default='card'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['cards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create note_links table
    op.create_table('note_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.String(), nullable=False),
        sa.Column('target_id', sa.String(), nullable=False),
        sa.Column('link_type', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['notes.id'], ),
        sa.ForeignKeyConstraint(['target_id'], ['notes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create event_logs table
    op.create_table('event_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('old_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('new_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for full-text search
    op.create_index('ix_cards_title', 'cards', ['title'], unique=False)
    op.create_index('ix_notes_title', 'notes', ['title'], unique=False)
    op.execute('CREATE INDEX ix_cards_content ON cards USING gin(to_tsvector(\'russian\', title || \' \' || coalesce(content::text, \'\')))')
    op.execute('CREATE INDEX ix_notes_content ON notes USING gin(to_tsvector(\'russian\', title || \' \' || coalesce(content::text, \'\')))')


def downgrade() -> None:
    op.drop_index('ix_notes_content')
    op.drop_index('ix_cards_content')
    op.drop_index('ix_notes_title')
    op.drop_index('ix_cards_title')
    op.drop_table('event_logs')
    op.drop_table('note_links')
    op.drop_table('task_links')
    op.drop_table('files')
    op.drop_table('notes')
    op.drop_table('cards')