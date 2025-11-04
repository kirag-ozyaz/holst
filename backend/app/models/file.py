from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)  # Path relative to media root
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    base_card_id = Column(String, nullable=True)  # For general base card reference (will reference tasks since BaseCard is abstract)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    note_id = Column(String, ForeignKey("notes.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="files")
    note = relationship("Note", back_populates="files")