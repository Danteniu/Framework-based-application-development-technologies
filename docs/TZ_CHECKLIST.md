## Чек‑лист соответствия ТЗ — «СистемаКонтроля»

### Функциональные требования
- [x] **Регистрация и аутентификация**: `accounts/` (login/register), Django auth.
- [x] **Роли и доступ (менеджер/инженер/наблюдатель)**: `accounts/models.py` (`User.role`), проверки в `defects/views.py`, `projects/views.py`, `reports/views.py`.
- [x] **Проекты/объекты и этапы**: `projects/models.py`, страницы `projects/`.
- [x] **Дефекты (заголовок, описание, приоритет, исполнитель, сроки, вложения)**: `defects/models.py`, формы/страницы `defects/`.
- [x] **Статусы**: `defects/models.py` (state machine) + серверные проверки в `defects/views.py`.
- [x] **Комментарии и история изменений**: `DefectComment`, `DefectHistory` + записи через `defects/services.py`.
- [x] **Поиск/сортировка/фильтрация**: `defects/views.py` + UI `templates/defects/list.html`.
- [x] **Экспорт CSV/Excel**: `reports/views.py`, `reports/excel.py`.
- [x] **Аналитика**: `reports/dashboard` (график по статусам).

### Нефункциональные требования
- [x] **Отклик ≤ 1 сек (для 50 пользователей)**: есть сценарий нагрузочного теста `locustfile.py` + инструкция в `README.md`.
- [x] **Бэкап БД раз в сутки**: команда `python manage.py backup_db` (app `core`) + `scripts/backup.ps1` (Планировщик).
- [x] **RU интерфейс + адаптивность**: Bootstrap 5, `LANGUAGE_CODE=ru-ru`.
- [x] **Совместимость браузеров**: UI на Bootstrap + стандартный HTML.
- [x] **Пароли: argon2/bcrypt**: включён `Argon2PasswordHasher`.
- [x] **SQLi/XSS/CSRF**: ORM + autoescape + CSRF middleware.


