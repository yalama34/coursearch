# Пайплайн обучения CatBoost-моделей ранжирования курсов

## Назначение

Данный пайплайн реализует двухэтапное ранжирование образовательных курсов:

- **View Ranker** – предсказывает вероятность того, что пользователь **просмотрит или лайкнет** курс в течение **7 дней** после момента времени `T`. Выполняет широкий отбор кандидатов.
- **Like Ranker** – предсказывает вероятность **лайка** курса **после его просмотра** (внутри текущей сессии). Уточняет итоговый список.

Итоговый скор курса вычисляется как взвешенная сумма предсказаний View Ranker (коэффициент 0.6) и Like Ranker (коэффициент 0.4). При недостатке кандидатов от View Ranker (например, для новых пользователей) список дополняется популярностными курсами из модуля Top‑N.

## Цель экспериментов

- **View Ranker**: обучить модель, которая для каждого пользователя в момент времени `T` предскажет курсы, наиболее релевантные для просмотра/лайка в горизонте 7 дней. Основная метрика – **NDCG@10**.
- **Like Ranker**: обучить модель пост‑клик ранжирования, которая внутри сессии пользователя предскажет, какой из просмотренных курсов будет лайкнут в ближайшие **6 часов**. Основная метрика – **NDCG@5**.

## Входные данные

Пайплайн использует синтетические данные из директории `/content/drive/MyDrive/coursearch/` (или кэш‑директории). Необходимые файлы:

- `courses.json` – курсы (id, название, описание, сложность, возраст, домен)
- `users.json` – пользователи (id, предпочитаемая сложность)
- `actions_seed.json` – события (просмотры, лайки, timestamp)
- `junction_seed.json` – связи курсов и пользователей с тегами
- `taxonomy.json` – таксономия тегов (домены, кластеры, ко‑окуррентность)
- `cosine_distances.csv` – предвычисленные косинусные расстояния между пользователями и курсами

Также требуется **fine‑tuned sentence‑transformer** модель (`course-emb-v1`), которая генерирует эмбеддинги курсов и тегов. Модель должна быть размещена в той же директории.

## Выходные данные

После выполнения пайплайна в папке `like_ranker_v3/` сохраняются артефакты:

- `catboost_ranker.cbm` – обученная модель CatBoostRanker (Like Ranker)
- `scaler.pkl` – объект StandardScaler для нормализации признаков
- `feature_cols.json` – список признаков (61 фича)
- `model_metadata.json` – метаданные (метрики, гиперпараметры, дата обучения)
- `inference_example.py` – пример кода для инференса

Для View Ranker аналогичные артефакты сохраняются в `model_export_v2/`.

Кроме того, в процессе работы создаётся кэш‑директория `cached_data/` с промежуточными датасетами (`dataset_candidates.parquet`, `aux_dicts.pkl`), что ускоряет повторные запуски.


Готовые модели лежат в папках `view_ranker` (View Ranker) и `like_ranker_v3` (Like Ranker). Для инференса нужны три файла:

- `catboost_ranker.cbm` – модель
- `scaler.pkl` – нормализатор
- `feature_cols.json` – список признаков

**Запуск:**

### like_ranker:

```python
import json, pickle, pandas as pd
from catboost import CatBoostRanker

model = CatBoostRanker()
model.load_model("like_ranker_v3/catboost_ranker.cbm")

with open("like_ranker_v3/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open("like_ranker_v3/feature_cols.json", "r") as f:
    feature_cols = json.load(f)

# df_features — DataFrame с колонками из feature_cols
X_scaled = scaler.transform(df_features[feature_cols])
scores = model.predict(X_scaled)
```
### view ranker:

```python
import json, pickle, pandas as pd
from catboost import CatBoostRanker

model = CatBoostRanker()
model.load_model("view_ranker/catboost_ranker.cbm")

with open("view_ranker/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open("view_ranker/feature_cols.json", "r") as f:
    feature_cols = json.load(f)

# df_features — DataFrame с колонками из feature_cols
X_scaled = scaler.transform(df_features[feature_cols])
scores = model.predict(X_scaled) 
```
### Краткое описание моделей и признаков

#### View Ranker (44 признака)

**Поведенческие:**
* просмотры/лайки за 7/30 дней;
* тренд активности;
* энтропия тегов;
* длина сессии.

**Характеристики курса:**
* популярность (взвешенная сумма просмотров, лайков и новизны);
* возраст;
* количество тегов;
* сложность;
* домен.

**Теговые признаки:**
* Jaccard пересечения тегов;
* ко‑окуррентность тегов;
* близость доменов/кластеров.

**Эмбеддинговые признаки:**
* косинусное расстояние между динамическим эмбеддингом пользователя (экспоненциальное затухание за 30дней) и эмбеддингом курса;
* скалярное произведение;
* L2‑расстояние.

**История взаимодействия:**
* был ли курс просмотрен/лайкнут ранее;
* количество предыдущих просмотров;
* дни с последнего взаимодействия.

**Модель:**
```python
CatBoostRanker(
    loss_function='YetiRank',
    eval_metric='NDCG:top=10',
    iterations=1000,
    learning_rate=0.03,
    depth=6
)
```

### Like Ranker (61 признак)

**Добавлены сессионные признаки:**
- `duration_seconds` — длительность просмотра (сгенерирована эвристически);
- `time_since_last_like_seconds` — время с последнего лайка;
- `likes_in_last_3_views` — количество лайков среди последних трёх просмотров в сессии;
- `is_repeat_view` — повторный просмотр в сессии;
- `hour_of_day`, `is_weekend` — временные признаки.

**Модель:**
```python
CatBoostRanker(
    loss_function='YetiRankPairwise',
    eval_metric='NDCG:top=5',
    iterations=1000,
    learning_rate=0.05,
    depth=6,
    l2_leaf_reg=3,
    border_count=128
)
```
Группировка для ранжирования: group_id = f"{user_id}_{session_id}", где сессия разрывается при простое > 2 часов.

Метрики и результаты

View Ranker (валидация):

* NDCG@10 = 0.922;

* Precision@10 = 0.886;

* Recall@10 = 0.983.

Like Ranker (валидация, окно лайка 6 часов):

* NDCG@3 = 0.629;

* NDCG@5 = 0.687;

* NDCG@10 = 0.767;

* MAP@10 = 0.492;

* Precision@1 = 0.434.

#### Требования к окружению:
Python 3.12+;

библиотеки: catboost, sentence-transformers, pandas, numpy, scikit-learn, matplotlib, seaborn, pyarrow (для parquet);
