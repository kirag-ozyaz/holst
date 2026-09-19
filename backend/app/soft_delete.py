"""Soft-delete column sync for tasks and notes (non-Alembic DBs e.g. smoke tests)."""

from sqlalchemy import inspect, text

from .database import engine


def ensure_deleted_at_columns() -> None:
    insp = inspect(engine)
    if not insp.has_table("tasks") or not insp.has_table("notes"):
        return

    with engine.begin() as conn:
        for table in ("tasks", "notes"):
            cols = {c["name"] for c in insp.get_columns(table)}
            if "deleted_at" not in cols:
                conn.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN deleted_at TIMESTAMP")
                )
            conn.execute(
                text(
                    f"CREATE INDEX IF NOT EXISTS ix_{table}_deleted_at "
                    f"ON {table} (deleted_at)"
                )
            )
