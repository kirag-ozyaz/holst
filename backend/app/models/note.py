from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base_card import BaseCard

class Note(BaseCard):
    __tablename__ = "notes"

    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)  # Changed from card_id to task_id
    note_type = Column(String, default="note")  # To distinguish different types of notes
    
    # Relationships
    task = relationship("Task", back_populates="notes")
    files = relationship("File", back_populates="note")
    outgoing_links = relationship("NoteLink", foreign_keys="NoteLink.source_id", back_populates="source_note")
    incoming_links = relationship("NoteLink", foreign_keys="NoteLink.target_id", back_populates="target_note")