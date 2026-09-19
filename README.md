# Платформа Холст

Веб-приложение для **визуального планирования**: задачи и заметки на холсте, связи, граф, журнал задач.

**Продуктовое ТЗ:** [docs/TZ-v2.md](docs/TZ-v2.md)

**Техническая документация (актуальная):**

- [docs/README.md](docs/README.md) — оглавление
- [docs/architecture.md](docs/architecture.md) — архитектура и потоки
- [docs/classes.md](docs/classes.md) — модули и классы
- [docs/entities.md](docs/entities.md) — сущности и связи

Legacy ТЗ: [docs/Окончательное-Техническое-задание-на-платформу-Холст.md](docs/Окончательное-Техническое-задание-на-платформу-Холст.md) (не отражает текущий MVP; см. TZ-v2).

## Стек

- **Frontend:** Vue 3, Pinia, Konva.js, Cytoscape.js
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Инфраструктура:** Docker Compose, Nginx

## Запуск

```bash
docker compose up -d --build
```

Приложение: **http://localhost** (Nginx). Backend напрямую: порт **8000**, frontend: **3000**.

Сервисы Compose: `nginx`, `frontend`, `backend`, `db`, `voice-stt` (STT не входит в MVP UI; см. TZ-v2).

Пересборка отдельных сервисов: [docs/build_docker.md](docs/build_docker.md).

## Структура репозитория

```
backend/app/          main.py (API), models/, schemas/
frontend/src/         views/, components/, stores/, classes/, services/
nginx/                прокси /api, /media, SPA
docs/                 TZ-v2 + architecture, classes, entities
docs/archive/         устаревшие материалы
voice-stt/            опциональный контейнер распознавания речи
```

## API (кратко)

| Ресурс | Префикс |
|--------|---------|
| Задачи | `GET/POST /api/cards`, `PUT/DELETE /api/cards/{id}` |
| Заметки | `GET/POST /api/notes`, `PUT/DELETE /api/notes/{id}` |
| Связи задач | `GET/POST /api/task-links`, `DELETE /api/task-links/{id}` |
| Связи заметок | `GET/POST /api/note-links`, `DELETE /api/note-links/{id}` |
| Граф | `GET /api/graph` |
| Health | `GET /api/health` |

Поля `parent_id` (задачи), `task_id` (заметки), `link_target_type` (`task` \| `note`) — см. [docs/entities.md](docs/entities.md).

## Тесты

```bash
cd backend && python3 -m pytest tests/test_smoke.py
```

Frontend: `npm run build` в `frontend/` (unit-тесты в package.json могут отсутствовать).
