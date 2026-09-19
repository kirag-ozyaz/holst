# Структура классов и модулей

Краткая карта кода для навигации. Диаграммы PlantUML перенесены в [archive/diagrams-legacy/](archive/diagrams-legacy/) и могут быть неполными.

## Frontend (Vue 3 + Pinia)

### Компоненты

| Компонент | Файл | Ответственность |
|-----------|------|-----------------|
| `App.vue` | `src/App.vue` | Корень, `ThemeToggle`, `router-view` |
| `CanvasView` | `views/CanvasView.vue` | Toolbar + TaskJournal + Canvas + EditorPanel + подсказка режима связи |
| `GraphView` | `views/GraphView.vue` | Toolbar + TaskJournal + Cytoscape |
| `Toolbar` | `components/Toolbar.vue` | Создание задачи/заметки, режим «Связь», переход на граф |
| `Canvas` | `components/Canvas.vue` | Konva Stage/Layer, загрузка данных, рендер карточек и **стрелок** связей |
| `EditorPanel` | `components/EditorPanel.vue` | Редактирование, привязка заметок, список связей с подсветкой на холсте |
| `TaskJournal` | `components/TaskJournal.vue` | Дерево задач по `parent_id`, раскрытие подзадач |
| `ThemeToggle` | `components/ThemeToggle.vue` | Светлая / тёмная тема |

### Pinia stores

**`stores/canvas.js`**

- State: `cards`, `notes`, `taskLinks`, `noteLinks`, `selectedElement`, `highlightedLinkKey`, `linkPeerElementId`, `linkMode`, `pendingLinkSource`, transform viewport.
- Actions: CRUD карточек и заметок; `createTaskLink` / `createNoteLink`; `attachNoteToTask`, `detachNoteFromTask`, `createNoteForTask`, `setNoteParentTask`; `createLinkBetween` (режим «Связь»); `linksForElement`, `notesAttachedToTask`.

**`stores/theme.js`**

- `init()`, `toggle()`, `apply()` — атрибут `data-theme`, `localStorage` `holst-theme`.

### Konva-классы

```
CanvasElement (базовый)
├── TaskCard   — прямоугольник, type 'task'
└── NoteCard   — жёлтый стиль, type 'note'
```

| Класс | Файл | Поведение |
|-------|------|-----------|
| `CanvasElement` | `classes/CanvasElement.js` | Group, drag, select, link mode click, `setSelected` / `setLinkPeerHighlight` |
| `TaskCard` | `classes/TaskCard.js` | Визуал задачи |
| `NoteCard` | `classes/NoteCard.js` | Визуал заметки |

### Сервисы

**`CanvasElementService`** (`services/CanvasElementService.js`)

- `getMaxZIndex`, `bringToFront`, `getSortedElements` — порядок отрисовки на слое Konva.
- Делегирует сохранение координат в handlers из `Canvas.vue`.

### Точка входа

**`main.js`** — Pinia, router, патч Konva через `markRaw`, инициализация темы.

## Backend (FastAPI)

### Модули

| Путь | Содержимое |
|------|------------|
| `app/main.py` | Все HTTP-маршруты, бизнес-правила (циклы связей), upload файлов |
| `app/database.py` | Engine, Session, `get_db` |
| `app/models/` | SQLAlchemy-модели (см. [entities.md](entities.md)) |
| `app/schemas/` | Pydantic-схемы Task/Note (используются частично) |
| `tests/test_smoke.py` | Health, CRUD, parent_id, task→note link |

Отдельных классов «Service» / «Repository» **нет** — логика в функциях-обработчиках `main.py`.

## Соглашения API ↔ UI

- В REST по историческим причинам задачи называются **cards** (`/api/cards`), в БД таблица **`tasks`**.
- Тип элемента на фронте: `task` | `note`; в graph API узлы могут иметь `type: "card"`.

## Дальнейшее (по TZ-v2, не реализовано)

Подзадачи в UI кроме журнала, «сделать подзадачей» на холсте, отдельные router-модули backend — см. фазы в TZ-v2.
