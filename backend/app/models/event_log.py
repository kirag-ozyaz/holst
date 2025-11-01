from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func
from ..database import Base

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)  # create, update, delete, link, unlink
    entity_type = Column(String, nullable=False)  # card, note, file, link
    entity_id = Column(String, nullable=False)
    user_id = Column(String, nullable=True)  # For future multi-user support
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(Text, nullable=True)  # Additional context