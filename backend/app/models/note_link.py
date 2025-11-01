from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

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