# Деплой на Timeweb (виртуальный хостинг + Python)

Эта инструкция рассчитана на классический виртуальный хостинг Timeweb (панель «Хостинг → Сайты»). Все пути приводятся относительно аккаунта вида `/home/<логин>/web/<домен>/public_html`.

## 1. Создаём сайт и включаем Python

1. В панели Timeweb перейдите в **Хостинг → Сайты** и добавьте домен или поддомен.
2. Откройте созданный сайт → вкладка **Python** → включите поддержку Python и выберите нужную версию (рекомендуем 3.10+).
3. Запомните директорию `public_html` — туда нужно загрузить проект.

## 2. Загружаем код

1. Локально подготовьте архив/репозиторий с проектом (вся папка репозитория).
2. Загрузите файлы в `~/web/<домен>/public_html` (через файловый менеджер, SFTP или `scp`).
3. Проверьте, что в `public_html` лежат:
   - `app/`, `migrations/`, `instance/` (если нужна SQLite-база)
   - `index.wsgi`, `.htaccess`, `requirements.txt`, `create_admin.py`, `seed_data.py`, `env.example.txt`
   - `venv/` **не** загружаем — создаём на сервере.

## 3. Виртуальное окружение и зависимости

```bash
cd ~/web/<домен>/public_html
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Настраиваем `.env`

Создайте файл `.env` (из `env.example.txt`):

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<сгенерируйте токен: python generate_secret_key.py>
DATABASE_URL=sqlite:///student_rating.db  # или своя БД
```

Файл должен лежать рядом с `index.wsgi`. Права: `chmod 644 .env`.

## 5. База данных и данные по умолчанию

```bash
source venv/bin/activate
flask db upgrade
python seed_data.py
```

Для SQLite убедитесь, что `student_rating.db` создан (лежит в корне проекта) и права `chmod 644 student_rating.db`.

## 6. Создаём администратора

```bash
source venv/bin/activate
python create_admin.py        # интерактивно
# или
python create_admin.py --auto # создаёт admin / random-pass
```

Сохраните логин/пароль.

## 7. WSGI и .htaccess

Мы уже добавили файлы под Timeweb:

- `.htaccess` включает `Options +ExecCGI` и переписывает запросы в `index.wsgi`.
- `index.wsgi` активирует `venv`, подгружает `.env` и создаёт приложение через `create_app()`.

Если меняете структуру, убедитесь, что пути в `index.wsgi` указывают на актуальную папку, а файл имеет права `chmod 755 index.wsgi`.

## 8. Права и статика

```bash
chmod 755 .
chmod 755 index.wsgi wsgi.py
chmod -R 755 app/
```

Статичные файлы обслуживаются Flask'ом из `app/static/`. При необходимости можно настроить отдельный Alias в `.htaccess`, но для начала достаточно стандартной конфигурации.

## 9. Проверка

1. Откройте `https://<домен>/` — должна загрузиться главная страница.
2. Проверьте `https://<домен>/admin/login`.
3. Если видите страницу Timeweb «Сайт не настроен» — очистите кеш браузера или подождите, пока обновится конфигурация (до 5 минут).

## 10. Логи и отладка

- Логи находятся в `~/logs/<домен>.error.log` и `~/logs/<домен>.access.log`.
- Для оперативного просмотра:
  ```bash
  tail -n 100 ~/logs/<домен>.error.log
  ```
- Частые причины 500:
  - забыли активировать `venv` и установить зависимости;
  - `.env` отсутствует или нет `SECRET_KEY`;
  - неверные права на `index.wsgi` / `.env`;
  - модуль не найден (перезапустите Python в панели или обновите зависимости).

## 11. Альтернатива: Timeweb Cloud Apps

Если удобнее автоматический деплой:

1. В панели Timeweb Cloud → **Apps** → создать приложение → тип **Flask**.
2. Подключите репозиторий (GitHub/GitLab/Bitbucket) или загрузите архив.
3. Укажите команду запуска `gunicorn wsgi:app --bind 0.0.0.0:8000`.
4. Задайте переменные окружения (как в `.env`) через интерфейс.
5. Запустите деплой — сервис сам поднимет контейнер и выдаст URL или привяжет ваш домен.

## 12. Чек-лист

- [ ] Файлы загружены в `public_html`
- [ ] Создано и активировано `venv`
- [ ] Установлены зависимости из `requirements.txt`
- [ ] Создан `.env` с `SECRET_KEY` и `DATABASE_URL`
- [ ] Выполнены `flask db upgrade` и `python seed_data.py`
- [ ] Запущен `create_admin.py`
- [ ] Применены права на `index.wsgi`, `.env`, `app/`
- [ ] Логи чистые, сайт открывается

Готово! Теперь проект работает на Timeweb. Если понадобится другой способ деплоя (Docker, VPS, Cloud Apps) — адаптируйте шаги с учётом нужного окружения.

