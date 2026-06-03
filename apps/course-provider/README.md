# Course Provider

### Ответственность

- Масштабируемый сервис для добавления курсов из внешних источников в базу данных

---
### Структура

```
course-provider
└───src
    ├───common
    ├───db
    │   ├───models
    │   ├───repositories
    ├───dependencies
    ├───providers
    │   ├───stepik
    │   ├───udemy
    ├───quality
    │
    ├───schemas
```

### Запуск  
  
1. Запустить `docker-compose.yaml` / `docker-compose.dev.yaml`
2. `docker exec -it recsys_course_provider python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/sync?pages=150', data=b'')"`

---

## Архитектура

### Models
`/src/models`
Модели SQLAlchemy для базы данных PostgreSQL

### Providers
`/src/providers`
Синхронизация курсов из внешних источников с базой данных. Внешние источники курсов, каждый разделены на клиент и провайдер  

### Quality
`/src/quality`
Модуль, отвечающий за качество курсов, полученных от источника: отсутствие спама, очистка от html тегов