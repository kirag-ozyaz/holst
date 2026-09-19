# Диаграммы архитектуры платформы Холст

Все диаграммы созданы в формате PlantUML.

## Как просмотреть диаграммы

### Вариант 1: VS Code
1. Установите расширение [PlantUML](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml)
2. Откройте `.puml` файл
3. Нажмите `Ctrl+Shift+P` → `PlantUML: Preview Current`

### Вариант 2: Онлайн
1. Скопируйте содержимое файла
2. Вставьте на [plantuml.com/plantuml/uml](https://plantuml.com/plantuml/uml)

## Список диаграмм

| Диаграмма | Описание | Файл |
|-----------|----------|------|
| **Диаграмма классов** | Все модели backend и frontend, связи между ними | [`classes.puml`](classes.puml) |
| **Диаграмма компонентов** | Структура приложения, зависимости между модулями | [`components.puml`](components.puml) |
| **Создание задачи** | Последовательность: создание новой задачи через UI | [`api_create_task.puml`](api_create_task.puml) |
| **Перемещение (drag & drop)** | Последовательность: перемещение карточки на холсте | [`api_drag_drop.puml`](api_drag_drop.puml) |

## Технологии

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Vue 3 + Pinia + Konva.js (canvas) + Cytoscape.js (граф)
- **Инфраструктура**: Docker Compose, Nginx

> **Устарело:** актуальная схема — [../../architecture.md](../../architecture.md) и [../../classes.md](../../classes.md).

## Архитектура (историческая)

```
┌─────────────────────────────────────────────┐
│                 Nginx (:80)                  │
│  /api/ → Backend  │  / → Frontend           │
└──────────┬──────────────────┬────────────────┘
           │                  │
    ┌──────▼──────┐   ┌──────▼──────┐
    │   Backend   │   │  Frontend   │
    │  (:8000)    │   │  (:80/Nginx)│
    │  FastAPI    │   │  Vue 3      │
    └──────┬──────┘   └─────────────┘
           │
    ┌──────▼──────┐
    │  PostgreSQL │
    │   (:5432)   │
    └─────────────┘
```
