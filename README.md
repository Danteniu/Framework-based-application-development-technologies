## СистемаКонтроля — монолитное веб‑приложение (Django)

Веб‑система для управления дефектами на строительных объектах: роли пользователей, проекты/этапы, дефекты (статусы, приоритеты, сроки), комментарии, история изменений, вложения, отчёты (CSV/Excel), аналитика.

### Быстрый старт (Windows / PowerShell)

Установите Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Откройте:
- `http://127.0.0.1:8000/` — приложение
- `http://127.0.0.1:8000/admin/` — админка

### Роли
- **Менеджер**: назначает исполнителей/сроки, контролирует и формирует отчёты.
- **Инженер**: создаёт дефекты, ведёт работу по назначенным дефектам.
- **Наблюдатель**: просмотр прогресса и отчётности (без изменений).

### Примечания по безопасности
- Пароли хэшируются Argon2 (при наличии `argon2-cffi`).
- CSRF включён (стандарт Django).
- SQL‑инъекции предотвращаются использованием ORM.

### Резервное копирование БД (1 раз в сутки)
Для SQLite бэкап — копирование `db.sqlite3` в папку `backups/`.

Разовый запуск:

```powershell
.\.venv\Scripts\python manage.py backup_db --retention-days 14
```

Планировщик задач Windows (ежедневно):
- **Action**: `powershell.exe`
- **Arguments**: `-ExecutionPolicy Bypass -File scripts\backup.ps1 -RetentionDays 14`
- **Start in**: папка проекта

### Нагрузочное тестирование (критерий: отклик ≤ 1 сек)
Используйте Locust:

```powershell
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\locust -f locustfile.py --host http://127.0.0.1:8000
```

Откройте веб‑интерфейс Locust и задайте 50 пользователей (активных).

