# Настройка окружения для разработки

## Общие принципы разработки

Когда продукт уже работает в продакшене, для разработки нужно создать отдельное окружение с учетом следующих аспектов:

## 1. Отдельное окружение разработки

### Конфигурационные файлы
- Создайте отдельные файлы `docker-compose.dev.yml` для разработки
- Используйте `.env.dev` файлы для хранения переменных окружения разработки
- Не храните продакшен-ключи в файлах разработки

### База данных
- Используйте отдельную базу данных для разработки
- Вместо `POSTGRES_USER=holst` и `POSTGRES_PASSWORD=holst` используйте более безопасные значения
- Рассмотрите возможность использования SQLite для локальной разработки для упрощения настройки

## 2. Безопасность

### Учетные данные
```yaml
# docker-compose.dev.yml
services:
 db:
    environment:
      - POSTGRES_USER=dev_user
      - POSTGRES_PASSWORD=complex_dev_password
      - POSTGRES_DB=holst_dev
```

### Использование .env файлов
Создайте файл `.env.dev`:
```
DATABASE_URL=postgresql://dev_user:complex_dev_password@db:5432/holst_dev
SECRET_KEY=your_complex_dev_secret_key
DEBUG=true
```

## 3. Hot reloading и режим разработки

### Frontend
- Использовать режим разработки Vue.js с hot reloading
- Запускать фронтенд через `npm run serve` вместо production сборки
- Монтировать исходники в контейнер для мгновенного обновления

### Backend
- Включить режим отладки FastAPI
- Использовать auto-reload при изменении кода
- Добавить логирование для отладки

## 4. Разделение конфигураций

### Docker Compose для разработки
```yaml
# docker-compose.dev.yml
name: holst-dev

services:
  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=dev_user
      - POSTGRES_PASSWORD=complex_dev_password
      - POSTGRES_DB=holst_dev
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5433:5432"  # Использовать другой порт, чтобы не конфликтовать с продакшеном

  backend:
    build:
      context: ./backend
      target: development  # Отдельный stage в Dockerfile
    volumes:
      - ./backend:/app  # Монтирование исходников
    environment:
      - DATABASE_URL=postgresql://dev_user:complex_dev_password@db:5432/holst_dev
      - DEBUG=true
    ports:
      - "8000:8000"
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  frontend:
    build:
      context: ./frontend
      target: development
    volumes:
      - ./frontend:/app
      - /app/node_modules  # Исключить node_modules из монтирования
    ports:
      - "3001:8080"  # Использовать другой порт для разработки
    command: ["npm", "run", "serve"]
```

## 5. Управление зависимостями

### Отдельные файлы зависимостей
- `requirements.txt` - для продакшена
- `requirements-dev.txt` - для разработки (включая тестирование, отладку)
- `package.json` и `package-lock.json` для фронтенда

### Виртуальные окружения
- Использовать виртуальные окружения для изоляции зависимостей
- Использовать Poetry или pipenv для управления зависимостями

## 6. Тестирование

### Автоматизированные тесты
- Создать отдельные тестовые базы данных
- Писать unit-тесты для всех критических компонентов
- Использовать CI/CD pipeline для автоматического тестирования

### Тестовое окружение
```yaml
# docker-compose.test.yml
services:
  test-db:
    image: postgres:16
    environment:
      - POSTGRES_USER=test_user
      - POSTGRES_PASSWORD=test_password
      - POSTGRES_DB=holst_test
    volumes:
      - test_postgres_data:/var/lib/postgresql/data
```

## 7. Мониторинг и логирование

### Для разработки
- Более подробные логи
- Инструменты отладки
- Меньше агрегации логов
- Локальные инструменты мониторинга

## 8. Работа с Git

### Ветвление
- Использовать feature-ветки для новой функциональности
- Code review перед слиянием
- Автоматические тесты перед мержем

### .gitignore для разработки
```
# Virtual environments
.venv/
__pycache__/
*.pyc

# Environment variables
.env*
!.env.example

# IDE
.idea/
.vscode/
*.swp
*.swo

# Logs
*.log
logs/

# Development databases
*.db
```

## 9. Пример команд для запуска в режиме разработки

```bash
# Запуск в режиме разработки
docker-compose -f docker-compose.dev.yml up --build

# Запуск только необходимых сервисов
docker-compose -f docker-compose.dev.yml up db backend

# Запуск тестов
docker-compose -f docker-compose.test.yml run --rm backend pytest

# Миграции базы данных
docker-compose -f docker-compose.dev.yml run --rm backend alembic upgrade head
```

## 10. Дополнительные рекомендации

- Использовать pre-commit hooks для проверки кода
- Настроить автоматический форматирование кода
- Использовать статическую проверку типов
- Внедрить практику написания документации к коду
- Регулярно обновлять зависимости
- Проводить code review перед мержем