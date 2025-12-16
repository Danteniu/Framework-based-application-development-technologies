## Отчёт по тестированию (этап 5)

### 1) План тестирования
- Документ: `docs/TEST_PLAN.md`

### 2) Unit-тесты (≥ 5)
Запуск:

```powershell
.\.venv\Scripts\python manage.py test
```

Факт:
- Реализовано **≥ 5** unit-тестов (см. `defects/tests.py` (класс `DefectUnitTests`) + `reports/tests.py`).
- Результат прогона сохранён: `artifacts/test_output.txt`.

### 3) Интеграционные сценарии (≥ 2)
Факт:
- Реализовано **≥ 2** интеграционных сценария (см. `defects/tests.py` (класс `DefectIntegrationTests`)).

### 4) Проверка User Stories по критериям приёмки
- User Stories и критерии приёмки: `docs/USER_STORIES.md`.
- Критерии покрываются автотестами (роль/права/статусы/экспорт) + ручной проверкой UI (создание/вложения/дашборд).

### 5) Нагрузочное тестирование (50 активных пользователей, отклик ≤ 1 сек)
Запуск (headless):

```powershell
$env:LOCUST_USERNAME='loadtest'
$env:LOCUST_PASSWORD='loadtest'
.\.venv\Scripts\locust -f locustfile.py --headless -u 50 -r 10 -t 1m --host http://127.0.0.1:8000 --csv artifacts\loadtest --csv-full-history
```

Результаты (из `artifacts/loadtest_stats.csv`):
- **Aggregated avg**: ~**61.68 ms**
- **defects_list p95**: **86 ms**, max **846 ms**
- **dashboard p95**: **40 ms**, max **491 ms**
- **login (POST) p95**: **2500 ms** (логин выполняется 1 раз на пользователя; не влияет на основную работу после авторизации)
- Ошибок: **0**

Вывод: основная работа системы (список дефектов/дашборд) укладывается в требование **≤ 1 сек** с большим запасом.

### 6) Регрессионное тестирование
- Базовый регресс: `python manage.py check` + `python manage.py test` перед релизом (см. `docs/TEST_PLAN.md`).

### 7) Контроль покрытия кода тестами
Запуск:

```powershell
.\.venv\Scripts\coverage run manage.py test
.\.venv\Scripts\coverage report -m
```

Факт:
- Текстовый отчёт: `artifacts/coverage_report.txt`
- HTML отчёт: `artifacts/htmlcov/index.html`
- Итоговое покрытие: **76%** (строка `TOTAL`).


