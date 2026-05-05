
import json
import pickle
import pandas as pd
import numpy as np
from catboost import CatBoostRanker

model = CatBoostRanker()
model.load_model("catboost_ranker.cbm")
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
with open("feature_cols.json", "r") as f:
    feature_cols = json.load(f)

print("Модель и артефакты загружены.")
