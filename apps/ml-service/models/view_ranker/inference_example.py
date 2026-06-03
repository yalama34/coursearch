import json
import pickle
from catboost import CatBoostRanker

model = CatBoostRanker()
model.load_model("catboost_ranker.cbm")
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
with open("feature_cols.json", "r") as f:
    feature_cols = json.load(f)

with open("le_difficulty.pkl", "rb") as f:
    le_difficulty = pickle.load(f)

with open("le_domain.pkl", "rb") as f:
    le_domain = pickle.load(f)

