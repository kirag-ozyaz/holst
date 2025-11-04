from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class TaskLink(Base):
    __tablename__ = "task_links"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, ForeignKey("tasks.id"), nullable=False)  # Changed from cards.id
    target_id = Column(String, nullable=True) # Can reference both tasks and notes
    link_type = Column(String, nullable=False)  # depends_on, blocks, follows, related_to
    link_target_type = Column(String, default="task")  # "task" or "note"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_task = relationship("Task", foreign_keys=[source_id], back_populates="outgoing_links")
    # Note: target relationship will be determined dynamically based on link_target_type
    # For now, we'll keep a generic relationship that can point to either Task or Note
    target_task = relationship("Task", foreign_keys=[target_id], remote_side="Task.id", back_populates="incoming_links")