# AskMe

Учебный сервис вопросов и ответов на Django. Пользователи могут регистрироваться,
задавать вопросы, отвечать, голосовать, отмечать правильные ответы и искать
публикации по тегам.

## Возможности

- лента новых и популярных вопросов;
- вопросы, ответы и фильтрация по тегам;
- регистрация, авторизация и редактирование профиля;
- AJAX-голосование за вопросы и ответы;
- выбор правильного ответа автором вопроса;
- генератор данных для функционального и нагрузочного тестирования;
- конфигурации Gunicorn и nginx.

## Стек

- Python 3.10+
- Django 5.2 LTS
- PostgreSQL для production-like окружения, SQLite для локальной разработки
- Bootstrap 4, JavaScript
- Gunicorn, nginx

## Быстрый старт

```bash
git clone <repository-url>
cd ASKME_MOGILIN
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Приложение будет доступно по адресу <http://127.0.0.1:8000/>. Для локального
запуска переменные окружения не обязательны. Если потребуется изменить настройки,
скопируйте `.env.example` в `.env` и подключите его через IDE, Docker Compose,
`direnv` или другой менеджер окружения: Django не загружает `.env` автоматически.

Чтобы создать администратора:

```bash
python manage.py createsuperuser
```

Чтобы добавить небольшой демонстрационный набор данных:

```bash
python manage.py fill_db 10
```

Аргумент `ratio` создаёт `ratio` пользователей, `10 × ratio` вопросов,
`100 × ratio` ответов и `200 × ratio` голосов. Значение по умолчанию — `10000`,
поэтому для локального знакомства его следует указывать явно.

## PostgreSQL

Укажите переменные окружения перед миграциями:

```bash
export DB_ENGINE=postgresql
export DB_NAME=askme
export DB_USER=askme
export DB_PASSWORD=change-me
export DB_HOST=127.0.0.1
export DB_PORT=5432
python manage.py migrate
```

Полный список настроек находится в [`.env.example`](.env.example).

## Проверки

```bash
python manage.py check
python manage.py test
python -m compileall app askme_mogilin
```

Эти же проверки выполняются в GitHub Actions для Python 3.10 и 3.12.

## Документация

- [Архитектура](docs/ARCHITECTURE.md)
- [Разработка и эксплуатация](docs/DEVELOPMENT.md)
- [Нагрузочные замеры](docs/BENCHMARKS.md)
- [Правила внесения изменений](CONTRIBUTING.md)

## Структура проекта

```text
app/                 бизнес-логика, модели, формы и маршруты
askme_mogilin/       конфигурация Django, WSGI и ASGI
templates/           серверные HTML-шаблоны
static/              исходные CSS, JavaScript и изображения
benchmarks/          сценарии и сохранённые результаты замеров
simple_wsgi/         минимальное WSGI-приложение для сравнения
docs/                инженерная документация
askme.conf           пример конфигурации nginx
```

## Статус проекта

Проект предназначен для обучения и демонстрации. Перед публичным production-
развёртыванием необходимо задать собственный `DJANGO_SECRET_KEY`, отключить
`DJANGO_DEBUG`, настроить `DJANGO_ALLOWED_HOSTS`, HTTPS и внешнее хранилище
пользовательских файлов.

Лицензия пока не указана; по умолчанию права на исходный код сохраняются за
автором.
