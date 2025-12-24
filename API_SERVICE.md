# ML-сервис для предсказания цен на недвижимость

## Что это?

REST API на FastAPI который принимает данные о квартире и возвращает предсказанную цену. Модель - RandomForest, обучена на данных о недвижимости.

---

## Структура

```
app/
├── app.py              # основной файл, тут все эндпоинты
├── schemas.py          # pydantic схемы для валидации
├── database.py         # подключение к sqlite
├── models.py           # sqlalchemy модель истории
├── auth.py             # jwt авторизация
├── requirements.txt    # зависимости
├── alembic.ini         # конфиг миграций
├── alembic/            # папка с миграциями
│   ├── env.py
│   └── versions/
├── ml/
│   ├── model_loader.py # загрузка модели
│   └── inference.py    # предсказание
└── model/
    └── model.pkl       # сама модель
```

---

## Как запустить

```bash
# 1. ставим зависимости
cd app
pip install -r requirements.txt

# 2. накатываем миграции
alembic upgrade head

# 3. запускаем
python -m uvicorn app:app --reload --port 8000
```

Документация: http://localhost:8000/docs

---

## Эндпоинты

### POST /forward - предсказание

Кидаем json с данными квартиры, получаем цену.

```bash
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"Цена": 5000000, "Площадь": 50, ...}'
```

Ответ:
```json
{"prediction": {"prediction": 5234567.89}}
```

Ошибки:
- 400 - кривой запрос
- 403 - модель не смогла обработать

---

### GET /history - история запросов

Возвращает все предыдущие запросы из бд.

```bash
curl http://localhost:8000/history
```

Можно добавить пагинацию: `?skip=0&limit=10`

---

### DELETE /history - очистка истории

Нужен токен в заголовке.

```bash
curl -X DELETE http://localhost:8000/history \
  -H "X-Delete-Token: delete-history-secret-token"
```

---

### GET /stats - статистика

Среднее время обработки, квантили, инфа по запросам.

```bash
curl http://localhost:8000/stats
```

Ответ:
```json
{
  "processing_time": {
    "mean": 12.5,
    "percentile_50": 10.2,
    "percentile_95": 25.3,
    "percentile_99": 45.1
  },
  "input_stats": {
    "total_requests": 100,
    "successful_requests": 95,
    "failed_requests": 5,
    ...
  }
}
```

---

### POST /login - авторизация

Получаем jwt токен.

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

### Админские эндпоинты

`GET /admin/history` и `DELETE /admin/history` - то же самое что обычные, но нужен jwt токен админа в заголовке Authorization.

```bash
curl http://localhost:8000/admin/history \
  -H "Authorization: Bearer <токен>"
```

---

## Тестовые данные

| что | значение |
|-----|----------|
| логин | admin |
| пароль | admin123 |
| токен удаления | delete-history-secret-token |

---

## Alembic (миграции)

```bash
# применить миграции
alembic upgrade head

# откатить
alembic downgrade -1

# текущая версия
alembic current

# создать новую миграцию (после изменения models.py)
alembic revision --autogenerate -m "описание"
```

---

## Стек

- FastAPI - веб фреймворк
- Pydantic - валидация
- SQLAlchemy + SQLite - бд
- Alembic - миграции
- PyJWT - токены
- scikit-learn - модель
- numpy - массивы
