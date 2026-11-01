# NormDev — учет времени и цифровая концентрация

Десктоп-приложение для Windows: учет рабочего времени по проектам и задачам, анализ активности
и временное ограничение отвлекающих сайтов и программ.

- Учет времени и аналитика — Закусилов Денис (`app/timetracking`)
- Цифровая концентрация — Григорьева Анна (`app/focus`)
- Общая часть (БД, модели, главное окно) — `app/core`

## Стек

Python 3.12, PySide6, SQLite + SQLAlchemy, Alembic, psutil, pywin32.

## Запуск

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m app.main
```

Блокировка сайтов в первой версии вносит изменения в файл `hosts`, поэтому для проверки
блокировки приложение запускается из терминала, открытого от имени администратора.

База данных создается при первом запуске: `%LOCALAPPDATA%\NormDev\normdev.db`.
Другой файл можно указать переменной окружения `NORMDEV_DB`.

## Тесты и проверка кода

```powershell
.venv\Scripts\python -m pytest
.venv\Scripts\ruff check .
.venv\Scripts\ruff format .
```

## Миграции базы данных

Схема БД меняется только через миграции Alembic; при запуске приложение само применяет новые
миграции. После изменения моделей:

```powershell
.venv\Scripts\alembic revision --autogenerate -m "описание изменения"
```

Созданный файл в `app/migrations/versions` нужно просмотреть перед коммитом. Тест
`test_migrations_match_models` не пройдет, если модели изменены без миграции.

## Структура

```
app/
  core/          БД, общие модели (проекты, задачи, настройки), события таймера, главное окно
  timetracking/  учет времени
  focus/
    domain/      профили, правила, сессии
    blocker/     блокировка сайтов и программ
    ui/          интерфейс концентрации
  migrations/    миграции Alembic
tests/
```
