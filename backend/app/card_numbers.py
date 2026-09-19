"""Sequential numbers and created_at backfill for tasks and notes."""

from datetime import datetime, timezone

from sqlalchemy import func, inspect, text
from sqlalchemy.orm import Session

from .database import engine
from .models import Note, Task


def ensure_number_columns() -> None:
    """Add `number` column to tasks/notes when DB predates Alembic migration (e.g. smoke tests)."""
    insp = inspect(engine)
    if not insp.has_table("tasks") or not insp.has_table("notes"):
        return

    with engine.begin() as conn:
        for table in ("tasks", "notes"):
            cols = {c["name"] for c in insp.get_columns(table)}
            if "number" not in cols:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN number INTEGER"))

        conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_tasks_number ON tasks (number) "
                "WHERE number IS NOT NULL"
            )
        )
        conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_notes_number ON notes (number) "
                "WHERE number IS NOT NULL"
            )
        )


def backfill_numbers_and_dates(db: Session) -> None:
    """Assign numbers by creation order; set missing created_at to now (UTC)."""
    now = datetime.now(timezone.utc)

    for model in (Task, Note):
        missing_date = (
            db.query(model)
            .filter(model.created_at.is_(None))
            .all()
        )
        for row in missing_date:
            row.created_at = now

        unnumbered = (
            db.query(model)
            .filter(model.number.is_(None))
            .order_by(model.created_at.asc(), model.id.asc())
            .all()
        )
        if not unnumbered:
            continue

        max_num = db.query(model.number).filter(model.number.isnot(None)).order_by(model.number.desc()).first()
        next_num = (max_num[0] if max_num and max_num[0] is not None else 0) + 1
        for row in unnumbered:
            row.number = next_num
            next_num += 1

    db.commit()


def next_task_number(db: Session) -> int:
    max_num = db.query(func.max(Task.number)).scalar()
    return (int(max_num) if max_num is not None else 0) + 1


def next_note_number(db: Session) -> int:
    max_num = db.query(func.max(Note.number)).scalar()
    return (int(max_num) if max_num is not None else 0) + 1
