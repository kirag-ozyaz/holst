from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Card(Base):
    __tablename__ = "cards"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(JSON, default=list)  # Rich text content
    x = Column(Integer, default=0)
    y = Column(Integer, default=0)
    width = Column(Integer, default=300)
    height = Column(Integer, default=200)
    parent_id = Column(String, ForeignKey("cards.id"), nullable=True)  # For subcards
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    subcards = relationship("Card", backref="parent", remote_side=[id])
    notes = relationship("Note", back_populates="card")
    files = relationship("File", back_populates="card")
    outgoing_links = relationship("TaskLink", foreign_keys="TaskLink.source_id", back_populates="source_card")