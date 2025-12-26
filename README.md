# Weather Web

Веб-приложение для просмотра погоды сохраненных локаций.

## Технологии

**Core:**
- Python 3.13
- Django 5
- PostgreSQL
- Pydantic
- Bootstrap 5

**Dev:**
- uv
- pytest
- mypy
- ruff

## Запуск проекта

### 1. Предварительные требования
- PostgreSQL
- uv

### 2. Установка
```bash
git clone https://github.com/pocamest/weather-web.git
cd weather-web
uv sync
```

### 3. Настройка
```bash
cp .env.example .env
```

На основе примера заполните `.env`

### 4. Старт
```bash
uv run python manage.py migrate
uv run python manage.py runserver
```