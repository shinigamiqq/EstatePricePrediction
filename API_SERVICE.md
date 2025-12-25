# API сервис для предсказания цен недвижимости

## Описание

Это REST API сервис на FastAPI для предсказания стоимости квадратного метра недвижимости. В качестве ML модели используется Random Forest, обученный на собранном датасете новостроек.

Сервис сохраняет историю запросов в SQLite базу данных и предоставляет статистику по времени обработки.

## Структура проекта

```
app/
├── app.py              # главный файл с эндпоинтами
├── schemas.py          # pydantic схемы
├── database.py         # подключение к БД
├── models.py           # ORM модель для истории
├── auth.py             # JWT авторизация
├── requirements.txt    # зависимости
├── alembic.ini         # настройки миграций
├── alembic/
│   ├── env.py
│   └── versions/       # файлы миграций
├── ml/
│   ├── model_loader.py # загрузка артефактов модели
│   └── inference.py    # логика предсказания
└── model/
    └── model.pkl       # обученная модель + scaler + список фичей
```

## Установка и запуск

```bash
cd app

# установка зависимостей
pip install -r requirements.txt

# применение миграций БД
alembic upgrade head

# запуск сервера
python -m uvicorn app:app --reload --port 8000
```

После запуска доступна документация Swagger UI: http://localhost:8000/docs

## API эндпоинты

### POST /forward

Основной эндпоинт для получения предсказания. Принимает JSON с параметрами квартиры.

Пример запроса:
```bash
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{
    "Цена": 5000000,
    "Город": "Москва",
    "Площадь": 50,
    "Этаж": 10,
    "is_class_comfort": true,
    ...
  }'
```

Ответ (предсказанная цена за м²):
```json
{
  "prediction": {
    "prediction": 116058.41
  }
}
```

Коды ответов:
- 200 - успешное предсказание
- 400 - неверный формат запроса (bad request)
- 403 - модель не смогла обработать данные

### GET /history

Возвращает историю всех запросов к модели. Данные хранятся в SQLite.

```bash
curl http://localhost:8000/history
```

Поддерживается пагинация через параметры `skip` и `limit`:
```bash
curl "http://localhost:8000/history?skip=0&limit=20"
```

### DELETE /history

Удаляет всю историю запросов. Требуется токен подтверждения в заголовке.

```bash
curl -X DELETE http://localhost:8000/history \
  -H "X-Delete-Token: delete-history-secret-token"
```

### GET /stats

Возвращает статистику по запросам: среднее время обработки, квантили (50%, 95%, 99%), информация о входных данных.

```bash
curl http://localhost:8000/stats
```

Пример ответа:
```json
{
  "processing_time": {
    "mean": 74.5,
    "percentile_50": 65.2,
    "percentile_95": 120.3,
    "percentile_99": 150.1
  },
  "input_stats": {
    "total_requests": 50,
    "successful_requests": 48,
    "failed_requests": 2,
    "avg_input_length": 1440.5,
    "min_input_length": 1400,
    "max_input_length": 1500
  }
}
```

### POST /login

Авторизация для получения JWT токена.

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Админские эндпоинты

Для доступа к `/admin/history` (GET и DELETE) нужен JWT токен в заголовке Authorization:

```bash
curl http://localhost:8000/admin/history \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

## Тестовые данные для проверки

| Параметр | Значение |
|----------|----------|
| Логин | admin |
| Пароль | admin123 |
| Токен для удаления истории | delete-history-secret-token |

## Работа с миграциями (Alembic)

```bash
# применить все миграции
alembic upgrade head

# откатить последнюю миграцию
alembic downgrade -1

# посмотреть текущую версию
alembic current

# создать новую миграцию после изменения models.py
alembic revision --autogenerate -m "описание изменений"
```

## Используемые технологии

- **FastAPI** - веб-фреймворк для создания API
- **Pydantic** - валидация входных данных
- **SQLAlchemy** - ORM для работы с БД
- **SQLite** - база данных для хранения истории
- **Alembic** - миграции базы данных
- **PyJWT** - генерация и проверка JWT токенов
- **scikit-learn** - машинное обучение (Random Forest)
- **pandas** - обработка данных при инференсе
- **numpy** - работа с массивами

## Особенности реализации

1. Модель предсказывает логарифм цены за м², который затем преобразуется обратно через `np.expm1()`
2. При инференсе применяется тот же пайплайн что и при обучении: логарифмирование расстояний, one-hot encoding городов, масштабирование через StandardScaler
3. Все артефакты (модель, scaler, список признаков) хранятся в одном файле model.pkl
4. История запросов автоматически сохраняется в БД с временем обработки и статусом
