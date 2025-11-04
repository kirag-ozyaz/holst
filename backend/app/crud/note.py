from typing import List, Optional
from sqlalchemy.orm import Session
from .base import BaseCRUD
from ..models.note import Note
from ..schemas.note import NoteCreate, NoteUpdate


class NoteCRUD(BaseCRUD[Note]):
    def __init__(self):
        super().__init__(Note)

    def create_note(self, db: Session, note: NoteCreate) -> Note:
        return self.create(db, note)

    def update_note(self, db: Session, note_id: str, note_update: NoteUpdate) -> Optional[Note]:
        db_note = self.get(db, note_id)
        if db_note:
            return self.update(db, db_note, note_update)
        return None

    def delete_note(self, db: Session, note_id: str) -> bool:
        try:
            self.remove(db, note_id)
            return True
        except:
            return False

    def get_note_by_position(self, db: Session, x: int, y: int) -> Optional[Note]:
        """Получить заметку по координатам"""
        return self.get_by_position(db, x, y)


# Экземпляр для использования в других частях приложения
note_crud = NoteCRUD()

# Функции для совместимости с существующим кодом
def get_note(db: Session, note_id: str) -> Optional[Note]:
    return note_crud.get(db, note_id)


def get_notes(db: Session, skip: int = 0, limit: int = 100) -> List[Note]:
    return note_crud.get_multi(db, skip, limit)


def create_note(db: Session, note: NoteCreate) -> Note:
    return note_crud.create_note(db, note)


def update_note(db: Session, note_id: str, note_update: NoteUpdate) -> Optional[Note]:
    return note_crud.update_note(db, note_id, note_update)


def delete_note(db: Session, note_id: str) -> bool:
    return note_crud.delete_note(db, note_id)


def get_note_by_position(db: Session, x: int, y: int) -> Optional[Note]:
    return note_crud.get_note_by_position(db, x, y)