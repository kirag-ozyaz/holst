"""Add sequential number to tasks and notes

Revision ID: 004
Revises: 003
Create Date: 2026-09-19 20:10:00.000000

Numbering: tasks T-N, notes N-N (human-readable prefix applied in UI).
"""
import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def _backfill_table(connection, table: str) -> None:
    connection.execute(
        sa.text(f"UPDATE {table} SET created_at = NOW() WHERE created_at IS NULL")
    )
    rows = connection.execute(
        sa.text(
            f"SELECT id FROM {table} WHERE number IS NULL "
            f"ORDER BY created_at ASC NULLS LAST, id ASC"
        )
    ).fetchall()
    if not rows:
        return
    max_row = connection.execute(
        sa.text(f"SELECT COALESCE(MAX(number), 0) FROM {table}")
    ).scalar()
    next_num = int(max_row or 0) + 1
    for (row_id,) in rows:
        connection.execute(
            sa.text(f"UPDATE {table} SET number = :num WHERE id = :id"),
            {"num": next_num, "id": row_id},
        )
        next_num += 1


def upgrade() -> None:
    op.add_column("tasks", sa.Column("number", sa.Integer(), nullable=True))
    op.add_column("notes", sa.Column("number", sa.Integer(), nullable=True))
    op.create_index("ix_tasks_number", "tasks", ["number"], unique=True)
    op.create_index("ix_notes_number", "notes", ["number"], unique=True)

    connection = op.get_bind()
    _backfill_table(connection, "tasks")
    _backfill_table(connection, "notes")


def downgrade() -> None:
    op.drop_index("ix_notes_number", table_name="notes")
    op.drop_index("ix_tasks_number", table_name="tasks")
    op.drop_column("notes", "number")
    op.drop_column("tasks", "number")
