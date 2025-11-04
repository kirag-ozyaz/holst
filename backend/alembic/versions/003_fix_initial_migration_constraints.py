"""Fix initial migration constraints

Revision ID: 003
Revises: 002
Create Date: 2025-11-03 2:40:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Исправляем некорректные внешние ключи из начальной миграции
    # В таблице tasks (бывшая cards) есть внешний ключ parent_id, который ссылался на tasks.id
    # Это невозможно при создании таблицы, так как таблица еще не существует
    
    # Сначала удаляем некорректное ограничение
    try:
        op.drop_constraint('cards_parent_id_fkey', 'tasks', type_='foreignkey')
    except:
        # Если ограничение не существует или имеет другое имя, продолжаем
        pass
    
    # Создаем правильное ограничение
    op.create_foreign_key('tasks_parent_id_fkey', 'tasks', 'tasks', ['parent_id'], ['id'])
    
    # В начальной миграции в таблице notes также есть ошибка - внешний ключ task_id
    # ссылается на таблицу tasks, но в столбце указан card_id
    # Исправим это, если constraint все еще некорректен
    try:
        op.drop_constraint('notes_task_id_fkey', 'notes', type_='foreignkey')
    except:
        pass
    
    # Создаем правильный внешний ключ для notes.task_id
    op.create_foreign_key('notes_task_id_fkey', 'notes', 'tasks', ['task_id'], ['id'])
    
    # Также исправим ошибку в начальной миграции для таблицы files
    # Там внешний ключ task_id ссылался на таблицу tasks, но столбца task_id не было
    # Столбец был card_id, который мы переименовали в task_id
    try:
        op.drop_constraint('files_task_id_fkey', 'files', type_='foreignkey')
    except:
        pass
    
    # Создаем правильный внешний ключ для files.task_id
    op.create_foreign_key('files_task_id_fkey', 'files', 'tasks', ['task_id'], ['id'])
    
    # Внешний ключ для base_card_id не создаем, т.к. BaseCard - абстрактная модель


def downgrade() -> None:
    # Восстанавливаем предыдущее состояние
    # Нет внешнего ключа для base_card_id, т.к. BaseCard - абстрактная модель
    
    # Восстанавливаем внешние ключи
    op.drop_constraint('files_task_id_fkey', 'files', type_='foreignkey')
    op.drop_constraint('notes_task_id_fkey', 'notes', type_='foreignkey')
    op.drop_constraint('tasks_parent_id_fkey', 'tasks', type_='foreignkey')
    
    # Восстанавливаем старое ограничение (хотя оно было некорректным)
    # Это ограничение было некорректно в начальной миграции, но мы восстанавливаем его для совместимости
    try:
        op.create_foreign_key('cards_parent_id_fkey', 'tasks', 'tasks', ['parent_id'], ['id'])
    except:
        pass