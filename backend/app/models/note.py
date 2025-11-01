from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(JSON, default=list)  # Rich text content
    x = Column(Integer, default=0)
    y = Column(Integer, default=0)
    width = Column(Integer, default=300)
    height = Column(Integer, default=200)
    card_id = Column(String, ForeignKey("cards.id"), nullable=True)  # Optional link to card
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    card = relationship("Card", back_populates="notes")
    files = relationship("File", back_populates="note")
    outgoing_links = relationship("NoteLink", foreign_keys="NoteLink.source_id", back_populates="source_note")
    incoming_links = relationship("NoteLink", foreign_keys="NoteLink.target_id", back_populates="target_note")