import json
import pickle
import pandas as pd
import numpy as np
from catboost import CatBoostRanker

# Загрузка модели
model = CatBoostRanker()
model.load_model("catboost_ranker.cbm")

# Загрузка scaler
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# Загрузка списка признаков
with open("feature_cols.json", "r") as f:
    feature_cols = json.load(f)

print("Модель и артефакты загружены.")
print(f"Ожидает {len(feature_cols)} признаков")
