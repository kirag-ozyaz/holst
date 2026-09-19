# Сущности и модель данных

Таблицы PostgreSQL (имена в коде SQLAlchemy). Общие поля карточек вынесены в абстрактную модель **`BaseCard`**.

## ER-обзор (логический)

```
Task (tasks) ──parent_id──► Task          # иерархия подзадач
     │
     ├──1:N──► Note (notes.task_id)      # владение / «привязка»
     ├──1:N──► File (files.task_id)
     │
     ├──1:N──► TaskLink (source_id)      # исходящие связи
     └──1:N──► TaskLink (target_id)      # входящие (target = task или note*)

Note ──1:N──► NoteLink (source/target)    # связи заметка↔заметка
     └──1:N──► File (files.note_id)

* target_id в TaskLink для link_target_type=note ссылается на notes.id;
  FK на tasks для target_id в модели частично ослаблен на уровне приложения.
```

## Task (`tasks`)

Наследует **BaseCard**.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string (UUID) | PK |
| `title` | string | Заголовок |
| `content` | JSON | Тело (массив/JSON; plain в UI) |
| `x`, `y` | int | Позиция на холсте |
| `z_index` | int | Порядок слоя |
| `width`, `height` | int | Размер на холсте |
| `parent_id` | string?, FK → tasks.id | Родительская задача (журнал, дерево) |
| `task_type` | string | По умолчанию `"task"` |
| `number` | int | Порядковый номер задачи (отображение **T-{number}**) |
| `created_at`, `updated_at` | datetime | Метки времени (`created_at` — дата создания на карточке и в журнале) |
| `deleted_at` | datetime? | Мягкое удаление: не null — скрыто с холста и из списков API |

**Связи ORM:** `subtasks`, `files`, `notes`, `outgoing_links`, `incoming_links`.

На холсте размер карточки (`width`, `height`) меняется маркерами Konva и сохраняется через `PUT /api/cards/{id}`. Иерархия подзадач — поле `parent_id` (ПКМ на карточке задачи).

## Note (`notes`)

Наследует **BaseCard**.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | PK |
| (поля BaseCard) | | x, y, title, content, … |
| `task_id` | string?, FK → tasks.id | **Привязка** к задаче (владение) |
| `note_type` | string | По умолчанию `"note"` |
| `number` | int | Порядковый номер заметки (**N-{number}**) |

При «привязать заметку» в UI выставляются **`task_id`** и запись в **`task_links`** (задача → заметка) для линии на холсте.

## TaskLink (`task_links`)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | int | PK |
| `source_id` | string, FK → tasks.id | Источник (всегда задача) |
| `target_id` | string | Задача или заметка |
| `link_target_type` | string | `"task"` \| `"note"` (legacy alias `"card"` → task) |
| `link_type` | string | Напр. `depends_on` |
| `created_at` | datetime | |

Направление на UI: **source → target** (стрелка на холсте и в графе). Для задач проверяется отсутствие циклов среди рёбер task→task.

## NoteLink (`note_links`)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | int | PK |
| `source_id`, `target_id` | string, FK → notes.id | |
| `link_type` | string | Напр. `linked_to` |
| `created_at` | datetime | |

## File (`files`)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | int | PK |
| `filename`, `filepath`, `file_size`, `mime_type` | | Метаданные файла |
| `task_id` | string?, FK → tasks.id | Привязка к задаче |
| `note_id` | string?, FK → notes.id | Привязка к заметке |
| `base_card_id` | string? | Legacy / общая ссылка |
| `created_at` | datetime | |

Upload: `POST /api/cards/{card_id}/files`.

## EventLog (`event_logs`)

Таблица зарезервирована под аудит (create/update/link). В фазе 0–1 **не** заполняется из основных API handlers — модель есть для будущих фаз (auth, история).

## BaseCard (абстрактная)

Общие поля карточек для Task и Note — см. `backend/app/models/base_card.py`.

## API-имена vs сущности

| HTTP | Сущность |
|------|----------|
| `/api/cards` | Task |
| `/api/notes` | Note |
| `/api/task-links` | TaskLink |
| `/api/note-links` | NoteLink |
| `/api/graph` | Агрегат nodes + edges для визуализации |

## Миграции

Alembic: `backend/alembic/versions/` — переименование card→task, `parent_id`, `task_id` у notes.
