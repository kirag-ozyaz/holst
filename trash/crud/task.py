from typing import List, Optional
from sqlalchemy.orm import Session
from .base import BaseCRUD
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate


class TaskCRUD(BaseCRUD[Task]):
    def __init__(self):
        super().__init__(Task)

    def create_task(self, db: Session, task: TaskCreate) -> Task:
        return self.create(db, task)

    def update_task(self, db: Session, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
        db_task = self.get(db, task_id)
        if db_task:
            return self.update(db, db_task, task_update)
        return None

    def delete_task(self, db: Session, task_id: str) -> bool:
        try:
            self.remove(db, task_id)
            return True
        except:
            return False

    def get_task_by_position(self, db: Session, x: int, y: int) -> Optional[Task]:
        """Получить задачу по координатам"""
        return self.get_by_position(db, x, y)


# Экземпляр для использования в других частях приложения
task_crud = TaskCRUD()

# Функции для совместимости с существующим кодом
def get_task(db: Session, task_id: str) -> Optional[Task]:
    return task_crud.get(db, task_id)


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    return task_crud.get_multi(db, skip, limit)


def create_task(db: Session, task: TaskCreate) -> Task:
    return task_crud.create_task(db, task)


def update_task(db: Session, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
    return task_crud.update_task(db, task_id, task_update)


def delete_task(db: Session, task_id: str) -> bool:
    return task_crud.delete_task(db, task_id)


def get_task_by_position(db: Session, x: int, y: int) -> Optional[Task]:
    return task_crud.get_task_by_position(db, x, y)