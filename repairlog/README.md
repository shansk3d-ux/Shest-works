# RepairLog

Веб-приложение для учёта ремонтов кухонного, бытового, промышленного и
ресторанного оборудования. Подробный план разработки — в корневом
документе плана проекта.

## Стек

Django 5, PostgreSQL 16, Django Templates + HTMX + Bootstrap 5, Docker Compose.

## Запуск локально (Docker)

1. Скопируйте `.env.example` в `.env` и при необходимости отредактируйте значения:

   ```bash
   cp .env.example .env
   ```

2. Соберите и запустите контейнеры:

   ```bash
   docker compose up --build
   ```

3. Примените миграции и создайте суперпользователя (в отдельном терминале):

   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```

4. Откройте <http://localhost:8000/> — должна открыться стартовая страница RepairLog.

## Разработка без Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # укажите DATABASE_URL для локальной БД или используйте sqlite по умолчанию
python manage.py migrate
python manage.py runserver
```

## Тесты и линтер

```bash
pytest
ruff check .
```

## pre-commit

```bash
pre-commit install
```

## Деплой и бэкапы

Инструкции по продакшен-запуску (Gunicorn + Caddy) и бэкапам появятся
на соответствующих этапах разработки (см. план проекта, шаги 9–10).
