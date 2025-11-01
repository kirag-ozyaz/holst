from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class TaskLink(Base):
    __tablename__ = "task_links"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, ForeignKey("cards.id"), nullable=False)
    target_id = Column(String, nullable=True)  # Will be updated to support both cards and notes
    link_type = Column(String, nullable=False)  # depends_on, blocks, follows, related_to
    link_target_type = Column(String, default="card")  # "card" or "note"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_card = relationship("Card", foreign_keys=[source_id], back_populates="outgoing_links")