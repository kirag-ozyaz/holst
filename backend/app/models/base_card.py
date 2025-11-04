from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class BaseCard(Base):
    """
    Базовая модель для карточек (задач и примечаний)
    """
    __abstract__ = True

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(JSON, default=list)  # Rich text content
    x = Column(Integer, default=0)
    y = Column(Integer, default=0)
    z_index = Column(Integer, default=0)  # Z-index for layering
    width = Column(Integer, default=300)
    height = Column(Integer, default=200)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Общие связи
    files = relationship("File", back_populates="base_card")