from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, ForeignKeyConstraint, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class TaskLink(Base):
    __tablename__ = "task_links"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    target_id = Column(String, nullable=True)  # Can reference both tasks and notes
    link_type = Column(String, nullable=False)  # depends_on, blocks, follows, related_to
    link_target_type = Column(String, default="task")  # "task" or "note"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Foreign key constraints
    __table_args__ = (
        ForeignKeyConstraint([target_id], ["tasks.id"], name="fk_task_links_target_task", ondelete="CASCADE"),
    )

    # Relationships
    source_task = relationship("Task", foreign_keys=[source_id], back_populates="outgoing_links")
    target_task = relationship("Task", foreign_keys=[target_id], remote_side="Task.id", back_populates="incoming_links")
