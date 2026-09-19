"""Add deleted_at for soft delete on tasks and notes

Revision ID: 005
Revises: 004
Create Date: 2026-09-19 20:30:00.000000
"""
import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "notes",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tasks_deleted_at", "tasks", ["deleted_at"], unique=False)
    op.create_index("ix_notes_deleted_at", "notes", ["deleted_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_notes_deleted_at", table_name="notes")
    op.drop_index("ix_tasks_deleted_at", table_name="tasks")
    op.drop_column("notes", "deleted_at")
    op.drop_column("tasks", "deleted_at")
