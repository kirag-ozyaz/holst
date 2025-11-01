# Платформа Холст

Платформа Холст — это веб-приложение для визуального планирования и управления задачами с поддержкой заметок, связей и графов.

## Архитектура

- **Frontend**: Vue.js 3, Konva.js, Cytoscape.js
- **Backend**: FastAPI, PostgreSQL, SQLAlchemy
- **Инфраструктура**: Docker, Docker Compose, Nginx

## Запуск

### Требования

- Docker
- Docker Compose

контейнеры
 - holst-backend (бэкенд приложения)
 - holst-nginx (Nginx сервер)
 - holst-voice-stt (сервис распознавания речи)
 - holst-frontend (фронтенд приложения)
 - holst-db (PostgreSQL база данных)

### Запуск в режиме разработки

```bash
docker-compose up --build
```

Приложение будет доступно по адресу `http://localhost`.

### Запуск в продакшене

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Структура проекта

```
.
├── backend/          # FastAPI приложение
│   ├── app/
│   │   ├── models/   # Модели SQLAlchemy
│   │   ├── schemas/  # Схемы Pydantic
│   │   └── main.py   # Основной файл приложения
│   └── requirements.txt
├── frontend/         # Vue.js приложение
│   ├── src/
│   │   ├── components/
│   │   └── views/
│   └── package.json
├── nginx/            # Конфигурация Nginx
├── voice-stt/        # Сервис распознавания речи
└── docker-compose.yml
```

## API

### Задачи

- `GET /api/cards` — получить все задачи
- `POST /api/cards` — создать задачу
- `PUT /api/cards/{id}` — обновить задачу
- `DELETE /api/cards/{id}` — удалить задачу

### Заметки

- `GET /api/notes` — получить все заметки
- `POST /api/notes` — создать заметку
- `PUT /api/notes/{id}` — обновить заметку
- `DELETE /api/notes/{id}` — удалить заметку

### Связи

- `GET /api/task-links` — получить все связи между задачами
- `POST /api/task-links` — создать связь между задачами
- `DELETE /api/task-links/{id}` — удалить связь

### Граф

- `GET /api/graph` — получить граф связей

## Тестирование

Для запуска тестов:

```bash
# Backend
cd backend
python -m pytest

# Frontend
cd frontend
npm run test
```

## Миграции

Для создания и применения миграций:

```bash
cd backend
alembic revision --autogenerate -m "Описание миграции"
alembic upgrade head