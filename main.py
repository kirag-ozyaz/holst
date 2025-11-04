from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os

# Настройка базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модели данных
class BaseCard(Base):
    """
    Базовая модель для карточек (задач и примечаний)
    """
    __abstract__ = True

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(JSON, default=list)  # Rich text content
    x = Column(Integer, default=0)
    y = Column(Integer, default=0)
    z_index = Column(Integer, default=0)  # Z-index for layering
    width = Column(Integer, default=300)
    height = Column(Integer, default=200)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Общие связи
    files = relationship("File", back_populates="base_card")


class Task(BaseCard):
    __tablename__ = "tasks"

    parent_id = Column(String, ForeignKey("tasks.id"), nullable=True)  # For subtasks
    task_type = Column(String, default="task")  # To distinguish different types of tasks
    
    # Relationships
    subtasks = relationship("Task", backref="parent", remote_side=[id])
    notes = relationship("Note", back_populates="task")
    outgoing_links = relationship("TaskLink", foreign_keys="TaskLink.source_id", back_populates="source_task")
    incoming_links = relationship("TaskLink", foreign_keys="TaskLink.target_id", back_populates="target_task")


class Note(BaseCard):
    __tablename__ = "notes"

    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)  # Changed from card_id to task_id
    note_type = Column(String, default="note")  # To distinguish different types of notes
    
    # Relationships
    task = relationship("Task", back_populates="notes")
    files = relationship("File", back_populates="note")
    outgoing_links = relationship("NoteLink", foreign_keys="NoteLink.source_id", back_populates="source_note")
    incoming_links = relationship("NoteLink", foreign_keys="NoteLink.target_id", back_populates="target_note")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)  # Path relative to media root
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    note_id = Column(String, ForeignKey("notes.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="files")
    note = relationship("Note", back_populates="files")


class TaskLink(Base):
    __tablename__ = "task_links"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, ForeignKey("tasks.id"), nullable=False)  # Changed from cards.id
    target_id = Column(String, nullable=True)  # Will be updated to support both tasks and notes
    link_type = Column(String, nullable=False)  # depends_on, blocks, follows, related_to
    link_target_type = Column(String, default="task")  # "task" or "note"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_task = relationship("Task", foreign_keys=[source_id], back_populates="outgoing_links")
    target_task = relationship("Task", foreign_keys=[target_id], back_populates="incoming_links")


class NoteLink(Base):
    __tablename__ = "note_links"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, ForeignKey("notes.id"), nullable=False)
    target_id = Column(String, ForeignKey("notes.id"), nullable=False)
    link_type = Column(String, default="linked_to")  # Always bidirectional
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_note = relationship("Note", foreign_keys=[source_id], back_populates="outgoing_links")
    target_note = relationship("Note", foreign_keys=[target_id], back_populates="incoming_links")


# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Маршруты API
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/tasks")
def create_task(task: dict):
    # Логика создания задачи
    db_task = Task(
        id=task.get("id"),
        title=task.get("title", ""),
        content=task.get("content", []),
        x=task.get("x", 0),
        y=task.get("y", 0),
        z_index=task.get("z_index", 0),
        width=task.get("width", 300),
        height=task.get("height", 200),
        parent_id=task.get("parent_id"),
        task_type=task.get("task_type", "task")
    )
    db = SessionLocal()
    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    finally:
        db.close()

@app.get("/api/tasks")
def get_tasks():
    # Логика получения задач
    db = SessionLocal()
    try:
        tasks = db.query(Task).all()
        return tasks
    finally:
        db.close()

@app.put("/api/tasks/{task_id}")
def update_task(task_id: str, task: dict):
    # Логика обновления задачи
    db = SessionLocal()
    try:
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        for key, value in task.items():
            setattr(db_task, key, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    finally:
        db.close()

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str):
    # Логика удаления задачи
    db = SessionLocal()
    try:
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        db.delete(db_task)
        db.commit()
        return {"message": "Task deleted successfully"}
    finally:
        db.close()

@app.post("/api/notes")
def create_note(note: dict):
    # Логика создания заметки
    db_note = Note(
        id=note.get("id"),
        title=note.get("title", ""),
        content=note.get("content", []),
        x=note.get("x", 0),
        y=note.get("y", 0),
        z_index=note.get("z_index", 0),
        width=note.get("width", 250),
        height=note.get("height", 150),
        task_id=note.get("task_id"),
        note_type=note.get("note_type", "note")
    )
    db = SessionLocal()
    try:
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note
    finally:
        db.close()

@app.get("/api/notes")
def get_notes():
    # Логика получения заметок
    db = SessionLocal()
    try:
        notes = db.query(Note).all()
        return notes
    finally:
        db.close()

@app.put("/api/notes/{note_id}")
def update_note(note_id: str, note: dict):
    # Логика обновления заметки
    db = SessionLocal()
    try:
        db_note = db.query(Note).filter(Note.id == note_id).first()
        if not db_note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        for key, value in note.items():
            setattr(db_note, key, value)
        
        db.commit()
        db.refresh(db_note)
        return db_note
    finally:
        db.close()

@app.delete("/api/notes/{note_id}")
def delete_note(note_id: str):
    # Логика удаления заметки
    db = SessionLocal()
    try:
        db_note = db.query(Note).filter(Note.id == note_id).first()
        if not db_note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        db.delete(db_note)
        db.commit()
        return {"message": "Note deleted successfully"}
    finally:
        db.close()

@app.post("/api/task-links")
def create_task_link(link: dict):
    # Логика создания связи задач
    db_link = TaskLink(
        source_id=link.get("source_id"),
        target_id=link.get("target_id"),
        link_type=link.get("link_type", "dependency")
    )
    db = SessionLocal()
    try:
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
        return db_link
    finally:
        db.close()

@app.post("/api/note-links")
def create_note_link(link: dict):
    # Логика создания связи заметок
    db_link = NoteLink(
        source_id=link.get("source_id"),
        target_id=link.get("target_id"),
        link_type=link.get("link_type", "linked_to")
    )
    db = SessionLocal()
    try:
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
        return db_link
    finally:
        db.close()

@app.get("/api/task-links")
def get_task_links():
    # Логика получения связей задач
    db = SessionLocal()
    try:
        links = db.query(TaskLink).all()
        return links
    finally:
        db.close()

@app.get("/api/note-links")
def get_note_links():
    # Логика получения связей заметок
    db = SessionLocal()
    try:
        links = db.query(NoteLink).all()
        return links
    finally:
        db.close()

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")