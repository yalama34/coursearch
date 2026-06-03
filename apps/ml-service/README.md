# ML Service

### Ответственность

- Масштабируемый пайплайн рекомендаций
- Индексация курсов
- Получение объяснения рекомендаций с помощью LLM


---
### Структура


```
ml-service
├───models
│   ├───course-emb-v1
│   ├───it-slang-model-v4
│   ├───like_ranker_v1
│   ├───like_ranker_v2
│   ├───like_ranker_v3
│   └───view_ranker
├───data
├───src
│   ├───common
│   ├───db
│   │   └───models
│   ├───domain
│   │   ├───enum
│   │   └───recommendation
│   ├───engine
│   ├───integrations
│   │   ├───llm
│   │   │   ├───prompts
│   │   │   └───services
│   ├───pipelines
│   │   ├───stages
│   ├───protocols
│   ├───routers
│   ├───schemas
│   ├───scripts
│   ├───services
│   └───utils
└───tests
    ├───integration
    │   └───db
    └───unit
        ├───engine
        ├───pipelines
        └───utils
```

### Запуск  
  
Запуск в `docker-compose.yaml` / `docker-compose.dev.yaml`

---

## Архитектура

### Models
`/models`
Актуальные и предыдущие версии моделей машинного обучения для рекомендаций

### LLM integration
`/src/integrations/llm`
Интеграция с облачной LLM для получения объяснений рекомендаций

### Pipelines
`/src/pipelines`
Содержит основные пайплайны: fine-tunning модели и ее валидация, индексация курсов, загрузка данных из csv, пайплайн рекомендаций

### Stages
`/src/pipelines/stages`
Стадии пайплайна рекомендаций

### Data
`/src/data`
Обработка данных из датасета в формате csv

### Engine
`/src/engine`
Движок для работы с эмбеддингами

### Routers
`/src/routers`
Ручки для обработки запросов от core-api. Отвечают за вызов пайплайна рекомендаций и LLM

### Services
`/src/services`
Сервисы для работы с базой данных и получением и кешированием объяснений рекомендаций

### Protocols
`/src/protocols`
Хранит протоколы для корректного взаимодействия между сервисами