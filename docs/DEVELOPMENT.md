# Разработка и эксплуатация

## Конфигурация

Настройки читаются из переменных окружения. Django не загружает `.env`
самостоятельно; его можно подключить через IDE, Docker Compose, systemd или
утилиту наподобие `direnv`.

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `DJANGO_SECRET_KEY` | небезопасный dev-ключ | подпись сессий и токенов |
| `DJANGO_DEBUG` | `true` | режим отладки |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | разрешённые Host-заголовки |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | пусто | доверенные HTTPS-origin через запятую |
| `DJANGO_TIME_ZONE` | `Europe/Moscow` | часовой пояс приложения |
| `DB_ENGINE` | `sqlite` | `sqlite` или `postgresql` |
| `DB_NAME` | `db.sqlite3` | файл SQLite или имя базы PostgreSQL |
| `DB_USER`, `DB_PASSWORD` | пусто | доступ к PostgreSQL |
| `DB_HOST`, `DB_PORT` | `127.0.0.1`, `5432` | адрес PostgreSQL |

## Типичный цикл разработки

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py runserver
```

После изменения моделей:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py test
```

Пользовательские файлы сохраняются в `uploads/`, собранная production-статика —
в `staticfiles/`. Оба каталога локальные и исключены из Git.

## Демонстрационные данные

Команда `fill_db` рассчитана в том числе на крупные нагрузочные наборы. Для
обычной разработки используйте небольшой коэффициент:

```bash
python manage.py fill_db 10
```

Команда добавляет данные к существующим. Перед повторным большим запуском
создайте отдельную тестовую базу. Не запускайте значение по умолчанию на рабочей
машине без оценки требуемого места: оно означает миллионы объектов.

## Запуск через Gunicorn

```bash
python manage.py collectstatic --noinput
gunicorn -c askme_mogilin/gunicorn-conf.py
```

Доступны `GUNICORN_BIND`, `GUNICORN_WORKERS` и `GUNICORN_TIMEOUT`. Логи Gunicorn
направляются в stdout/stderr, поэтому конфигурация подходит для systemd и
контейнеров.

Пример [`askme.conf`](../askme.conf) предполагает расположение проекта в
`/srv/askme`. Перед установкой замените домен и пути, проверьте конфигурацию
командой `nginx -t`, затем включите HTTPS. Динамические ответы намеренно не
кэшируются: они зависят от сессии пользователя.

## Production checklist

- задайте длинный случайный `DJANGO_SECRET_KEY`;
- установите `DJANGO_DEBUG=false` и точный `DJANGO_ALLOWED_HOSTS`;
- настройте PostgreSQL, резервное копирование и ротацию логов;
- настройте TLS и параметры secure-cookie на уровне Django;
- выполните `python manage.py check --deploy`;
- вынесите пользовательские загрузки в устойчивое хранилище;
- применяйте миграции до переключения трафика на новую версию.
