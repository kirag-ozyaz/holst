from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .base_card import BaseCardSchema


class NoteCreate(BaseCardSchema):
    task_id: Optional[str] = None
    note_type: str = "note"


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[List] = None
    x: Optional[int] = None
    y: Optional[int] = None
    z_index: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    task_id: Optional[str] = None


class Note(BaseCardSchema):
    task_id: Optional[str] = None
    note_type: str = "note"
    
    class Config:
        from_attributes = True


class NoteInDB(Note):
    pass