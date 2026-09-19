import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import engine, get_db
from .models import Task, Note, EventLog, File, NoteLink, TaskLink

# Create tables only if DB is available
import time

def create_tables_if_needed():
    """Создаёт таблицы только если подключение к БД доступно"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            Task.__table__.create(bind=engine, checkfirst=True)
            Note.__table__.create(bind=engine, checkfirst=True)
            File.__table__.create(bind=engine, checkfirst=True)
            TaskLink.__table__.create(bind=engine, checkfirst=True)
            NoteLink.__table__.create(bind=engine, checkfirst=True)
            EventLog.__table__.create(bind=engine, checkfirst=True)
            print("Tables created successfully")
            return
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} - Error creating tables: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                print("Warning: Could not connect to database. Tables will be created on first connection.")

create_tables_if_needed()

APP_VERSION = os.getenv("APP_VERSION", "0.1.0-phase-0-1")
APP_PHASE = os.getenv("APP_PHASE", "0-1")


def _resolve_built_at() -> str:
    env_value = os.getenv("APP_BUILT_AT", "").strip()
    if env_value:
        return env_value
    built_file = Path(__file__).resolve().parent.parent / ".built_at"
    if built_file.is_file():
        return built_file.read_text(encoding="utf-8").strip()
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


APP_BUILT_AT = _resolve_built_at()

app = FastAPI(title="Холст API", version=APP_VERSION)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:80", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
Path("static").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

# Create media directory
MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True)

# API Routes

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "version": APP_VERSION,
        "phase": APP_PHASE,
        "built_at": APP_BUILT_AT,
        "message": "Холст API работает",
    }

# Helper function to get next z_index
def get_next_z_index(db: Session):
    max_task_z = db.query(Task).order_by(Task.z_index.desc()).first()
    max_note_z = db.query(Note).order_by(Note.z_index.desc()).first()
    
    max_z = 0
    if max_task_z and max_task_z.z_index:
        max_z = max(max_z, max_task_z.z_index)
    if max_note_z and max_note_z.z_index:
        max_z = max(max_z, max_note_z.z_index)
    
    return max_z + 1

# Cards CRUD
@app.post("/api/cards")
def create_card(card_data: dict, db: Session = Depends(get_db)):
    card_id = str(uuid.uuid4())
    z_index = card_data.get("z_index", get_next_z_index(db))
    
    card = Task(
        id=card_id,
        title=card_data.get("title", "Новая задача"),
        content=card_data.get("content", []),
        x=card_data.get("x", 100),
        y=card_data.get("y", 100),
        z_index=z_index,
        width=card_data.get("width", 300),
        height=card_data.get("height", 200),
        parent_id=card_data.get("parent_id")
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card

@app.get("/api/cards")
def get_cards(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.get("/api/cards/{card_id}")
def get_card(card_id: str, db: Session = Depends(get_db)):
    card = db.query(Task).filter(Task.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Карточка не найдена")
    return card

@app.put("/api/cards/{card_id}")
def update_card(card_id: str, card_data: dict, db: Session = Depends(get_db)):
    card = db.query(Task).filter(Task.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Карточка не найдена")

    for key, value in card_data.items():
        if hasattr(card, key):
            setattr(card, key, value)

    db.commit()
    db.refresh(card)
    return card

@app.delete("/api/cards/{card_id}")
def delete_card(card_id: str, db: Session = Depends(get_db)):
    card = db.query(Task).filter(Task.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Карточка не найдена")

    db.delete(card)
    db.commit()
    return {"message": "Карточка удалена"}

# Notes CRUD
@app.post("/api/notes")
def create_note(note_data: dict, db: Session = Depends(get_db)):
    note_id = str(uuid.uuid4())
    z_index = note_data.get("z_index", get_next_z_index(db))
    
    note = Note(
        id=note_id,
        title=note_data.get("title", "Новая заметка"),
        content=note_data.get("content", []),
        x=note_data.get("x", 100),
        y=note_data.get("y", 100),
        z_index=z_index,
        width=note_data.get("width", 300),
        height=note_data.get("height", 200),
        task_id=note_data.get("task_id") or note_data.get("card_id")
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@app.get("/api/notes")
def get_notes(db: Session = Depends(get_db)):
    return db.query(Note).all()

@app.get("/api/notes/{note_id}")
def get_note(note_id: str, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return note

@app.put("/api/notes/{note_id}")
def update_note(note_id: str, note_data: dict, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    for key, value in note_data.items():
        if hasattr(note, key):
            setattr(note, key, value)

    db.commit()
    db.refresh(note)
    return note

@app.delete("/api/notes/{note_id}")
def delete_note(note_id: str, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    db.delete(note)
    db.commit()
    return {"message": "Заметка удалена"}

def _task_link_would_cycle(db: Session, source_id: str, target_id: str) -> bool:
    """True if adding edge source -> target closes a cycle among tasks."""
    stack = [target_id]
    visited = set()
    while stack:
        node = stack.pop()
        if node == source_id:
            return True
        if node in visited:
            continue
        visited.add(node)
        links = db.query(TaskLink).filter(
            TaskLink.source_id == node,
            TaskLink.link_target_type == "task",
        ).all()
        for link in links:
            if link.target_id:
                stack.append(link.target_id)
    return False


# Task Links
@app.post("/api/task-links")
def create_task_link(link_data: dict, db: Session = Depends(get_db)):
    source_id = link_data["source_id"]
    target_id = link_data["target_id"]
    link_target_type = link_data.get("link_target_type", "task")
    if link_target_type == "card":
        link_target_type = "task"
    
    # Validate that source and target exist
    source_card = db.query(Task).filter(Task.id == source_id).first()
    if not source_card:
        raise HTTPException(status_code=404, detail="Source card not found")
    
    if link_target_type == "task":
        target_card = db.query(Task).filter(Task.id == target_id).first()
        if not target_card:
            raise HTTPException(status_code=404, detail="Target card not found")
        if source_id == target_id:
            raise HTTPException(status_code=400, detail="Cannot link task to itself")
        if _task_link_would_cycle(db, source_id, target_id):
            raise HTTPException(status_code=400, detail="Link would create a cycle")
    elif link_target_type == "note":
        target_note = db.query(Note).filter(Note.id == target_id).first()
        if not target_note:
            raise HTTPException(status_code=404, detail="Target note not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid link_target_type")
    
    # For note links, we don't enforce the foreign key constraint
    # so we need to handle this differently in the database
    link = TaskLink(
        source_id=source_id,
        target_id=target_id,
        link_type=link_data.get("link_type", "depends_on"),
        link_target_type=link_target_type
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link

@app.get("/api/task-links")
def get_task_links(db: Session = Depends(get_db)):
    return db.query(TaskLink).all()

@app.delete("/api/task-links/{link_id}")
def delete_task_link(link_id: int, db: Session = Depends(get_db)):
    link = db.query(TaskLink).filter(TaskLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Связь не найдена")

    db.delete(link)
    db.commit()
    return {"message": "Связь удалена"}

# Note Links
@app.post("/api/note-links")
def create_note_link(link_data: dict, db: Session = Depends(get_db)):
    link = NoteLink(
        source_id=link_data["source_id"],
        target_id=link_data["target_id"],
        link_type=link_data.get("link_type", "linked_to")
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link

@app.get("/api/note-links")
def get_note_links(db: Session = Depends(get_db)):
    return db.query(NoteLink).all()

@app.delete("/api/note-links/{link_id}")
def delete_note_link(link_id: int, db: Session = Depends(get_db)):
    link = db.query(NoteLink).filter(NoteLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Связь не найдена")

    db.delete(link)
    db.commit()
    return {"message": "Связь удалена"}

# Files
@app.post("/api/cards/{card_id}/files")
def upload_card_file(card_id: str, file: UploadFile = File(), db: Session = Depends(get_db)):
    # Check if card exists
    card = db.query(Task).filter(Task.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Карточка не найдена")

    # Save file
    file_path = MEDIA_DIR / f"{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create file record
    file_record = File(
        filename=file.filename,
        filepath=str(file_path),
        file_size=file_path.stat().st_size,
        mime_type=file.content_type,
        task_id=card_id
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    return file_record

@app.get("/api/files/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db)):
    file_record = db.query(File).filter(File.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="Файл не найден")

    return {"url": f"/media/{Path(file_record.filepath).name}"}

# Z-index management
@app.get("/api/max-z-index")
def get_max_z_index(db: Session = Depends(get_db)):
    """Get the maximum z_index across all cards and notes"""
    return {"max_z_index": get_next_z_index(db) - 1}

# Search
@app.get("/api/search")
def search(q: str, db: Session = Depends(get_db)):
    # Simple search implementation
    cards = db.query(Task).filter(Task.title.ilike(f"%{q}%")).all()
    notes = db.query(Note).filter(Note.title.ilike(f"%{q}%")).all()
    return {"cards": cards, "notes": notes}

# Graph
@app.get("/api/graph")
def get_graph(db: Session = Depends(get_db)):
    cards = db.query(Task).all()
    notes = db.query(Note).all()
    task_links = db.query(TaskLink).all()
    note_links = db.query(NoteLink).all()

    nodes = []
    edges = []

    # Add cards as nodes
    for card in cards:
        nodes.append({
            "id": card.id,
            "label": card.title,
            "type": "card",
            "x": card.x,
            "y": card.y
        })

    # Add notes as nodes
    for note in notes:
        nodes.append({
            "id": note.id,
            "label": note.title,
            "type": "note",
            "x": note.x,
            "y": note.y
        })

    # Add task links as edges
    for link in task_links:
        edges.append({
            "source": link.source_id,
            "target": link.target_id,
            "type": link.link_type,
            "target_type": link.link_target_type
        })

    # Add note links as edges
    for link in note_links:
        edges.append({
            "source": link.source_id,
            "target": link.target_id,
            "type": link.link_type
        })

    return {"nodes": nodes, "edges": edges}