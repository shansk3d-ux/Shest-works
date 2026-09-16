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

5. Заполните справочники начальными данными (типы оборудования, категории,
   популярные бренды):

   ```bash
   docker compose exec web python manage.py seed
   ```

## Разработка без Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # укажите DATABASE_URL для локальной БД или используйте sqlite по умолчанию
python manage.py migrate
python manage.py runserver
```

## Задачи и уведомления

Раздел «Задачи» (`/tasks/`) отделён от заявок на ремонт, но задачу можно
опционально привязать к заявке из списка. У задачи есть название,
описание, дата/время и три действия: «Завершить», «Отложить» (открывает
поле «Отложить до» с датой и временем) и «Отменить».

Пока открыта вкладка приложения в браузере, JS раз в минуту опрашивает
`/tasks/due/` и для наступивших задач показывает браузерное уведомление
(нужно разрешение Notification API) и проигрывает звук — на выбор
«Стандартный», «Колокольчик», «Перезвон» или «Тревога» (файлы в
`static/sounds/`). Уведомление по каждой задаче отправляется один раз;
при откладывании задачи флаг отправки сбрасывается автоматически.

## Поиск

Глобальный поиск (`/search/`, строка поиска в шапке) ищет по симптомам,
диагнозам и выполненным работам заявок, а также по базе знаний (симптом,
причина, решение), используя полнотекстовый поиск PostgreSQL
(`SearchVector`/`SearchRank`, конфигурация `russian`) плюс точное
совпадение по коду ошибки. Работает только на PostgreSQL — на SQLite
(дефолт `DATABASE_URL` для быстрой локальной разработки без БД) поиск
вызовет ошибку, для него нужна реальная PostgreSQL, как в
`docker-compose.yml`.

## Тесты и линтер

```bash
pytest
ruff check .
```

## pre-commit

```bash
pre-commit install
```

## Деплой

Продакшен-стек: Gunicorn (Django) + Caddy (реверс-прокси и автоматический
HTTPS по протоколу ACME) + PostgreSQL, всё в `docker-compose.prod.yml`.

1. На сервере укажите DNS-запись домена на его IP и откройте порты 80/443
   (нужны Caddy для выпуска сертификата Let's Encrypt).

2. Скопируйте `.env.example` в `.env` и заполните для продакшена:

   ```bash
   cp .env.example .env
   ```

   Обязательно замените: `DEBUG=False`, `SECRET_KEY` — на случайную
   строку, `ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS` — на реальный домен
   (`CSRF_TRUSTED_ORIGINS=https://ваш-домен`), `POSTGRES_PASSWORD` — на
   надёжный пароль, `DOMAIN` — на домен для Caddy. `SECURE_SSL_REDIRECT`
   уже включён по умолчанию в `config/settings/prod.py`.

3. Соберите и запустите:

   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

   При старте контейнер `web` сам применяет миграции и собирает
   статику (`deploy/entrypoint.sh`) перед запуском Gunicorn; Caddy
   раздаёт `staticfiles/` и `media/` напрямую и проксирует остальные
   запросы на Gunicorn.

4. Создайте суперпользователя и заполните справочники:

   ```bash
   docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
   docker compose -f docker-compose.prod.yml exec web python manage.py seed
   ```

5. Включайте `SECURE_HSTS_SECONDS` (например, `604800` — неделя) только
   после того как убедитесь, что HTTPS стабильно работает: HSTS запрещает
   браузеру обращаться к сайту по HTTP на указанный срок.

## Бэкапы

Инструкции по резервному копированию появятся на соответствующем этапе
разработки (см. план проекта, шаг 10).
