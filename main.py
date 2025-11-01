from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Настройка базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модели данных
class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(JSON, default=list)
    x = Column(Integer, default=0)
    y = Column(Integer, default=0)
    width = Column(Integer, default=300)
    height = Column(Integer, default=200)
    notes = relationship("Note", back_populates="task")

class Note(Base):
    __tablename__ = "notes"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(JSON, default=list)
    task_id = Column(String, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="notes")

class TaskLink(Base):
    __tablename__ = "task_links"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, ForeignKey("tasks.id"))
    target_id = Column(String, ForeignKey("tasks.id"))
    type = Column(String, default="dependency")

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
    return task

@app.get("/api/tasks")
def get_tasks():
    # Логика получения задач
    return []

@app.post("/api/notes")
def create_note(note: dict):
    # Логика создания заметки
    return note

@app.post("/api/task-links")
def create_task_link(link: dict):
    # Логика создания связи задач
    return link

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")