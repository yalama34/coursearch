# Backend core-api

### Ответственность 

- API for frontend
- Хранение данных в PostgreSQL
- Миграции
- 
---

### Структура

```
core-api/
├───migrations/
│   └───versions/
└───src/
    ├───db/
    │   ├───models/
    │   └───repositories/
    ├───dependencies/
    ├───domain/
    │   ├───constants/
    │   └───enum/
    ├───integrations/
    │   └───ml_service/
    ├───routers/
    ├───schemas/
    ├───services/
    └───workers/
```

### Запуск

1. Запуск в `docker-compose.yaml` / `docker-compose.dev.yaml`
2. Миграции запускаются отдельным сервисом `migrations, файлом ``migrate.sh``

--- 

## Архитектура

### Routers
`src/routers/`
Ручки для связи backend с frontend. Отвечают за входные/выходные данные запросов и корректный выброс ошибок из сервисов. Вызывают методы сервисов.

### Services
`src/services/`

Основная бизнес-логика запросов. Методы сервисов вызываются ручками. Взаимодействуют с PostgreSQL и Redis через репозитории, с сервисом рекомендаций через integrations.

### Repositories
`src/db/repositories/`

Точка взаимодействия с базой данных и кэш хранилищем. Методы репозиториев вызываются сервисами.

### Integrations 
`src/integrations/`

Интеграция внешних сервисов в core-api. Делает запросы ml-service api. Методы клиента вызываются сервисами. 

### Schemas
`src/schemas/` - схемы для routers

`integrations/ml_service/schemas.py` - схемы рекомендаций

Схемы валидации входных / выходных данных запросов. 

### Models
`src/db/models/`

Модели SQLAlchemy для базы данных PostgreSQL. 

### Migrations
`migrations/`

Управление миграциями с помощью Alembic. Хранение миграций.
