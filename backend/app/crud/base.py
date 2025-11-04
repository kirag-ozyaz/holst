from typing import List, Optional, Type, Generic, TypeVar
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.base_card import BaseCard

ModelType = TypeVar("ModelType", bound=BaseCard)


class BaseCRUD(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: str) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in) -> ModelType:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: str) -> ModelType:
        obj = db.query(self.model).get(id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        db.delete(obj)
        db.commit()
        return obj

    def get_by_position(self, db: Session, x: int, y: int) -> Optional[ModelType]:
        """Получить объект по координатам"""
        return db.query(self.model).filter(self.model.x == x, self.model.y == y).first()
    
    def get_next_z_index(self, db: Session) -> int:
        """Получить следующий z_index"""
        max_z = db.query(func.max(self.model.z_index)).scalar()
        return (max_z or 0) + 1