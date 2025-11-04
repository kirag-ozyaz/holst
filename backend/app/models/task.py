from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base_card import BaseCard


class Task(BaseCard):
    __tablename__ = "tasks"

    parent_id = Column(String, ForeignKey("tasks.id"), nullable=True)  # For subtasks
    task_type = Column(String, default="task") # To distinguish different types of tasks
    
    # Relationships
    subtasks = relationship("Task", backref="parent", remote_side=[id])
    notes = relationship("Note", back_populates="task")
    outgoing_links = relationship("TaskLink", foreign_keys="TaskLink.source_id", back_populates="source_task")
    incoming_links = relationship("TaskLink", foreign_keys="TaskLink.target_id", back_populates="target_task")