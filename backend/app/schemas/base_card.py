from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class BaseCardSchema(BaseModel):
    """
    Базовая схема для карточек (задач и примечаний)
    """
    id: Optional[str] = None
    title: str
    content: List = []
    x: int = 0
    y: int = 0
    z_index: int = 0
    width: int = 300
    height: int = 200
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None