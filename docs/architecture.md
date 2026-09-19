# Архитектура платформы «Холст» (фаза 0–1)

Документ описывает **фактическую** реализацию в репозитории на ветке с PR #4 (холст, граф, привязка заметок, журнал задач, тема). Планируемое — только со ссылкой на [TZ-v2.md](TZ-v2.md).

## Контейнеры (Docker Compose)

Сервисы в `docker-compose.yml`:

| Сервис | Роль | Порт (хост) |
|--------|------|-------------|
| **nginx** | Единая точка входа: `/` → frontend, `/api/` → backend, `/static/`, `/media/` | **80** |
| **frontend** | Статическая сборка Vue 3 (Nginx внутри образа) | 3000 (опционально напрямую) |
| **backend** | FastAPI, REST `/api/*` | 8000 (опционально напрямую) |
| **db** | PostgreSQL 16 | только внутри сети Docker |
| **voice-stt** | Отдельный сервис STT; прокси `/api/voice/` | 5000 |

Тома: `postgres_data`, `static_volume`, `media_volume`. Backend монтирует `./backend` в `/app` для разработки.

**Нет** в репозитории: `docker-compose.prod.yml`, отдельного API-gateway, микросервисного backend.

## Поток запроса (типичный сценарий)

```
Браузер
  → Nginx :80
       /        → frontend (Vue SPA)
       /api/*   → backend:8000 (FastAPI)
       /media/* → файлы с диска backend
  ← JSON / статика
```

Frontend ходит в API по относительному пути `/api/...` (тот же origin через Nginx).

### Загрузка холста

1. `Canvas.vue` при монтировании вызывает `canvasStore.loadData()` — параллельно `GET /api/cards`, `/api/notes`, `/api/task-links`, `/api/note-links`.
2. Konva рисует `TaskCard` / `NoteCard`, стрелки по `task_links` и `note_links`.
3. Редактирование → `PUT` на карточку/заметку; связи → `POST/DELETE` link endpoints.

### Режим графа

`GraphView.vue` — те же данные из Pinia, визуализация **Cytoscape.js** (`GET` не дублируется, если store уже загружен).

## Backend

- **Точка входа:** `backend/app/main.py` — все маршруты в одном модуле (нет пакета `routers/`, нет слоя `services/`).
- **ORM:** SQLAlchemy, модели в `backend/app/models/`.
- **Схемы Pydantic:** `backend/app/schemas/` (частично; create/update часто через `dict` в handlers).
- **БД:** PostgreSQL; таблицы также создаются при старте через `create_tables_if_needed()` (для dev/smoke допустим SQLite через `DATABASE_URL`).
- **Файлы:** каталог `media/` на backend, раздача через Nginx `/media/`.
- **Health:** `GET /api/health` — version, phase, built_at.

Проверка циклов при связях задач: `_task_link_would_cycle()` в `main.py`.

## Frontend

| Слой | Расположение | Назначение |
|------|--------------|------------|
| Views | `frontend/src/views/` | `CanvasView`, `GraphView` — композиция экрана |
| Components | `frontend/src/components/` | Toolbar, Canvas, EditorPanel, TaskJournal, ThemeToggle |
| Stores (Pinia) | `frontend/src/stores/` | `canvas.js` — данные и API; `theme.js` — тема |
| Classes | `frontend/src/classes/` | Konva: `CanvasElement`, `TaskCard`, `NoteCard` |
| Services | `frontend/src/services/` | `CanvasElementService` — z-index, сортировка |
| Router | `frontend/src/router/` | `/`, `/graph` |

Состояние холста централизовано в **`useCanvasStore`**: CRUD, связи, привязка заметок (`task_id` + `task_links`), режим «Связь», подсветка выбранной связи.

Тема: CSS-переменные на `document.documentElement[data-theme]`, ключ `localStorage` `holst-theme`.

## Что сознательно не в этой фазе

См. [TZ-v2.md](TZ-v2.md): auth, rich text (Tiptap), полноценный export, AI, голос в UI как core. Контейнер `voice-stt` есть в Compose, но **не** является частью MVP-потока редактора.

## Связанные документы

- [classes.md](classes.md) — классы и модули подробнее  
- [entities.md](entities.md) — таблицы и связи  
- [build_docker.md](build_docker.md) — пересборка  
