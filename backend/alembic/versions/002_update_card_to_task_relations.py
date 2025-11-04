"""Update card to task relations

Revision ID: 002
Revises: 001
Create Date: 2025-11-03 22:38:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Переименовываем таблицу cards в tasks
    op.rename_table('cards', 'tasks')
    
    # Обновляем столбец card_id на task_id в таблице files
    op.alter_column('files', 'card_id', new_column_name='task_id')
    # Создаем новый внешний ключ
    op.create_foreign_key('files_task_id_fkey', 'files', 'tasks', ['task_id'], ['id'])
    
    # Также добавляем столбец base_card_id для связи с общей базовой таблицей (без внешнего ключа, т.к. BaseCard абстрактная)
    op.add_column('files', sa.Column('base_card_id', sa.String(), nullable=True))
    
    # Обновляем внешний ключ в таблице notes (изменим card_id на task_id)
    op.drop_constraint('notes_task_id_fkey', 'notes', type_='foreignkey')
    op.alter_column('notes', 'card_id', new_column_name='task_id')
    op.create_foreign_key('notes_task_id_fkey', 'notes', 'tasks', ['task_id'], ['id'])
    
    # Обновляем внешние ключи в таблице task_links
    op.drop_constraint('task_links_source_id_fkey', 'task_links', type_='foreignkey')
    op.create_foreign_key('task_links_source_id_fkey', 'task_links', 'tasks', ['source_id'], ['id'])
    
    # Обновляем значение по умолчанию для link_target_type
    op.alter_column('task_links', 'link_target_type', server_default='task')
    
    # Обновляем индексы
    op.drop_index('ix_cards_title', table_name='tasks')
    op.drop_index('ix_cards_z_index', table_name='tasks')
    op.create_index('ix_tasks_title', 'tasks', ['title'])
    op.create_index('ix_tasks_z_index', 'tasks', ['z_index'])
    op.execute('DROP INDEX ix_cards_content')
    op.execute('CREATE INDEX ix_tasks_content ON tasks USING gin(to_tsvector(\'russian\', title || \' \' || coalesce(content::text, \'\')))')
    
    # Создаем индекс для task_id в таблице notes
    op.create_index('ix_notes_task_id', 'notes', ['task_id'])


def downgrade() -> None:
    # Восстанавливаем предыдущее состояние
    # Удаляем добавленный столбец base_card_id (без внешнего ключа)
    op.drop_column('files', 'base_card_id')
    
    # Обновляем индексы обратно
    op.execute('DROP INDEX ix_tasks_content')
    op.execute('CREATE INDEX ix_cards_content ON tasks USING gin(to_tsvector(\'russian\', title || \' \' || coalesce(content::text, \'\')))')
    op.drop_index('ix_tasks_z_index', table_name='tasks')
    op.drop_index('ix_tasks_title', table_name='tasks')
    op.create_index('ix_cards_z_index', 'tasks', ['z_index'])
    op.create_index('ix_cards_title', 'tasks', ['title'])
    
    # Удаляем индекс task_id из notes
    op.drop_index('ix_notes_task_id', table_name='notes')
    
    # Восстанавливаем внешний ключ в task_links
    op.drop_constraint('task_links_source_id_fkey', 'task_links', type_='foreignkey')
    op.create_foreign_key('task_links_source_id_fkey', 'task_links', 'tasks', ['source_id'], ['id'])
    
    # Восстанавливаем значение по умолчанию для link_target_type
    op.alter_column('task_links', 'link_target_type', server_default='card')
    
    # Восстанавливаем внешний ключ в таблице notes
    op.drop_constraint('notes_task_id_fkey', 'notes', type_='foreignkey')
    op.alter_column('notes', 'task_id', new_column_name='card_id')
    op.create_foreign_key('notes_task_id_fkey', 'notes', 'tasks', ['task_id'], ['id'])
    
    # Восстанавливаем внешний ключ в таблице files
    op.drop_constraint('files_task_id_fkey', 'files', type_='foreignkey')
    op.alter_column('files', 'task_id', new_column_name='card_id')
    op.create_foreign_key('files_task_id_fkey', 'files', 'tasks', ['task_id'], ['id'])
    
    # Переименовываем таблицу tasks обратно в cards
    op.rename_table('tasks', 'cards')