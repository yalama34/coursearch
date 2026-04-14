import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sentence_transformers import InputExample
from sklearn.model_selection import train_test_split

SYNTHETIC_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic"
RANDOM_STATE = 42

def df_to_input_examples(frame: pd.DataFrame) -> list[InputExample]:
    """
    Converts a pandas DataFrame into a list of InputExample objects.
    """
    return [
        InputExample(texts=[row.sent1, row.sent2], label=float(row.score))
        for row in frame.itertuples(index=False)
    ]

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the dataset by removing duplicates, invalid scores, and short texts.
    """
    df = df.dropna(subset=["sent1", "sent2", "score"]).copy()
    
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score"])
    df = df[(df["score"] >= 0.0) & (df["score"] <= 1.0)]
    
    df["sent1"] = df["sent1"].astype(str).str.strip().replace(r"\s+", " ", regex=True)
    df["sent2"] = df["sent2"].astype(str).str.strip().replace(r"\s+", " ", regex=True)
    
    df = df[(df["sent1"].str.len() > 5) & (df["sent2"].str.len() > 5)]
    
    df["_pair_id"] = df.apply(lambda row: tuple(sorted([row["sent1"], row["sent2"]])), axis=1)
    df = df.drop_duplicates(subset=["_pair_id"]).drop(columns=["_pair_id"])
    
    return df.reset_index(drop=True)

def analyze_distributions(df: pd.DataFrame) -> None:
    """
    Generates exploratory data analysis plots and prints basic statistics.
    """
    print(f"Total samples after cleaning: {len(df)}")
    print(df["category"].value_counts())
    
    len1 = df["sent1"].str.len()
    len2 = df["sent2"].str.len()
    
    print("\nСтатистика по длинне текстов (в символах):")
    print(pd.concat([len1, len2]).describe())
    
    plt.style.use("seaborn-v0_8-muted")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].hist(df["score"], bins=20, color="#3498db", edgecolor="white")
    axes[0].set_title("Распределение оценок", fontweight="bold")
    axes[0].set_xlabel("Оценка")
    axes[0].set_ylabel("Количество")
    
    axes[1].hist(len1, bins=30, alpha=0.6, label="Sentence 1", color="#2ecc71")
    axes[1].hist(len2, bins=30, alpha=0.6, label="Sentence 2", color="#e74c3c")
    axes[1].set_title("Распределение длинны текстов", fontweight="bold")
    axes[1].set_xlabel("Длинна (в символах)")
    axes[1].set_ylabel("Количество")
    axes[1].legend()
    
    plt.tight_layout()
    plot_path = SYNTHETIC_DIR.parent / "data_analysis.png"
    plt.savefig(plot_path)
    plt.close()
    print(f"\nГрафик распределений сохранен в {plot_path}")

def get_data_for_pipeline() -> list[list[InputExample] | pd.DataFrame]:
    """
    Parses synthetic data files, makes split to test|val|train and returns data for fine-tuning pipeline
    :return: [``train_examples``, ``val_examples``, ``df_test``], where
    ``train_examples`` and ``val_examples`` is a list of ``InputExample`` objects
    ``df_test`` is a pandas DataFrame containing the test data
    """
    dfs = []
    for category in ["A", "B", "C", "D", "E"]:
        path = SYNTHETIC_DIR / f"{category}.json"
        if path.exists():
            df_cur = pd.read_json(path)
            df_cur["category"] = category
            dfs.append(df_cur)

    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        df = clean_data(df)
        analyze_distributions(df)

        train_parts: list[pd.DataFrame] = []
        val_parts: list[pd.DataFrame] = []
        test_parts: list[pd.DataFrame] = []

        for category in sorted(df["category"].unique()):
            sub = df[df["category"] == category]
            if len(sub) < 3:
                continue

            train_val, test = train_test_split(
                sub, test_size=0.2, random_state=RANDOM_STATE, shuffle=True
            )
            train, val = train_test_split(
                train_val, test_size=0.25, random_state=RANDOM_STATE, shuffle=True
            )
            train_parts.append(train)
            val_parts.append(val)
            test_parts.append(test)

        df_train = pd.concat(train_parts, ignore_index=True) if train_parts else pd.DataFrame()
        df_val = pd.concat(val_parts, ignore_index=True) if val_parts else pd.DataFrame()
        df_test = pd.concat(test_parts, ignore_index=True) if test_parts else pd.DataFrame()

        train_examples = df_to_input_examples(df_train) if not df_train.empty else []
        val_examples = df_to_input_examples(df_val) if not df_val.empty else []
    else:
        df_test = pd.DataFrame()
        train_examples = []
        val_examples = []

    return [train_examples, val_examples, df_test]
