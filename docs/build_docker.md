Вот пошаговые команды для сборки и обновления Docker-контейнеров в проекте:

1. Пересборка фронтенд-контейнера:
   ```
   docker-compose build --no-cache frontend
   ```

2. Перезапуск фронтенд-сервиса:
   ```
   ы
   ```

3. Пересборка бэкенд-контейнера (с файлом main.py):
   ```
   docker-compose build --no-cache backend
   ```

4. Перезапуск бэкенд-сервиса:
   ```
   docker-compose up -d --no-deps backend
   ```

5. Перезапуск nginx-сервиса (если нужно обновить конфигурацию):
   ```
   docker-compose up -d --no-deps nginx
   ```

6. Если нужно обновить все сервисы проекта, можно использовать:
   ```
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

7. Для проверки статуса всех контейнеров:
   ```
   docker-compose ps
   ```

Эти команды позволят вам обновлять Docker-образы в проекте самостоятельно без участия.