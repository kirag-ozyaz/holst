from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

from .base_card import BaseCard


class Task(BaseCard):
    __tablename__ = "tasks"

    parent_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    task_type = Column(String, default="task")
    
    # Relationships
    files = relationship("File", back_populates="task", foreign_keys="File.task_id")
    subtasks = relationship("Task", backref="parent", remote_side="Task.id")
    notes = relationship("Note", back_populates="task")
    outgoing_links = relationship("TaskLink", foreign_keys="TaskLink.source_id", back_populates="source_task")
    incoming_links = relationship("TaskLink", foreign_keys="TaskLink.target_id", back_populates="target_task")