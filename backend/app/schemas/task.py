from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .base_card import BaseCardSchema


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


class TaskCreate(BaseCardSchema):
    parent_id: Optional[str] = None
    task_type: str = "task"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[List] = None
    x: Optional[int] = None
    y: Optional[int] = None
    z_index: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    parent_id: Optional[str] = None


class Task(BaseCardSchema):
    parent_id: Optional[str] = None
    task_type: str = "task"
    
    class Config:
        from_attributes = True


class TaskInDB(Task):
    pass