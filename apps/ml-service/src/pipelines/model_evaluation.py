import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, max_error
from scipy.stats import spearmanr, pearsonr
from sentence_transformers import SentenceTransformer, util
from sentence_transformers.evaluation import SentenceEvaluator


class ExtendedMetricsEvaluator(SentenceEvaluator):
    """
    Evaluates a SentenceTransformer model using multiple regression metrics.
    """
    def __init__(
            self,
            sentences1: list[str],
            sentences2: list[str],
            scores: list[float],
            batch_size: int = 16,
            main_similarity: str | None = "cosine",
            name: str = "",
            show_progress_bar: bool = False,
            write_csv: bool = True,
            penalty_coef: int | float = 0.5,
    ):
        super().__init__()
        self.sentences1 = sentences1
        self.sentences2 = sentences2
        self.scores = np.asarray(scores, dtype=np.float64)
        self.batch_size = batch_size
        self.main_similarity = main_similarity
        self.name = name
        self.show_progress_bar = show_progress_bar
        self.write_csv = write_csv
        self.primary_metric = f"{name}_spearman_cosine"
        self.penalty_coef = penalty_coef

    def __call__(self, model, output_path=None, epoch=-1, steps=-1) -> float:
        embeddings1 = model.encode(self.sentences1, convert_to_tensor=True)
        embeddings2 = model.encode(self.sentences2, convert_to_tensor=True)

        cosine_score = util.cos_sim(embeddings1, embeddings2).diag().cpu().numpy()
        cosine_val_score = self.scores

        mae = mean_absolute_error(cosine_val_score, cosine_score)
        rmse = np.sqrt(mean_squared_error(cosine_val_score, cosine_score))
        r2 = r2_score(cosine_val_score, cosine_score)
        max_err = max_error(cosine_val_score, cosine_score)
        spearman, _ = spearmanr(cosine_score, cosine_val_score)
        pearson, _ = pearsonr(cosine_score, cosine_val_score)

        print(f"MAE: {mae:.4f} | RMSE: {rmse:.4f} | R2: {r2:.4f} | Max Error: {max_err:.4f} | Spearman: {spearman:.4f} | Pearson: {pearson:.4f}")

        error_penalty = float(spearman) - (float(rmse) + max_err) / 2 * self.penalty_coef

        return error_penalty

def evaluate_and_plot(
        model: SentenceTransformer,
        df_test: pd.DataFrame,
        batch_size: int = 32
) -> None:
    """
    Evaluates model on test dataframe and generates performance plots.
    """
    s1 = df_test["sent1"].tolist()
    s2 = df_test["sent2"].tolist()
    gold = df_test["score"].to_numpy(dtype=np.float64)

    model.eval()
    with torch.no_grad():
        emb1 = model.encode(s1, batch_size=batch_size, show_progress_bar=False, convert_to_tensor=True)
        emb2 = model.encode(s2, batch_size=batch_size, show_progress_bar=False, convert_to_tensor=True)
        pred = util.cos_sim(emb1, emb2).diag().cpu().numpy()

    spearman, _ = spearmanr(pred, gold)
    pearson, _ = pearsonr(pred, gold)
    mae = mean_absolute_error(gold, pred)
    mse = mean_squared_error(gold, pred)
    r2 = r2_score(gold, pred)
    errors = pred - gold

    plt.style.use("seaborn-v0_8-muted")
    has_categories = "category" in df_test.columns
    fig, axes = plt.subplots(1, 3 if has_categories else 2, figsize=(18, 6))

    if not has_categories:
        axes = [axes[0], axes[1]]
    
    ax = axes[0]
    ax.scatter(gold, pred, alpha=0.4, s=20, color="#3498db", edgecolors="none")
    lims = [np.min([gold.min(), pred.min()]), np.max([gold.max(), pred.max()])]
    ax.plot(lims, lims, color="#e74c3c", linestyle="--", lw=2, label="Ideal (y=x)")
    ax.set_xlabel("Gold Score", fontsize=10)
    ax.set_ylabel("Predicted Score", fontsize=10)
    ax.set_title(f"Spearman: {spearman:.3f} | MAE: {mae:.3f} | R2: {r2:.3f}", fontsize=12, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend()

    ax = axes[1]
    ax.hist(errors, bins=35, color="#2ecc71", edgecolor="white", alpha=0.8)
    ax.axvline(0.0, color="#c0392b", linestyle="--", linewidth=1.5)
    ax.set_xlabel("Error (Pred - Gold)", fontsize=10)
    ax.set_ylabel("Count", fontsize=10)
    ax.set_title("Error Distribution", fontsize=12, fontweight="bold")
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    if has_categories:
        ax = axes[2]
        categories = sorted(df_test["category"].astype(str).unique())
        errors_by_cat = [errors[df_test["category"] == cat] for cat in categories]
        bp = ax.boxplot(errors_by_cat, labels=categories, patch_artist=True, showfliers=True, medianprops={"color": "black", "linewidth": 1.5})
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(categories)))
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.8)
        ax.set_ylabel("Error Magnitude", fontsize=10)
        ax.set_xlabel("Category", fontsize=10)
        ax.set_title("Errors by Category", fontsize=12, fontweight="bold")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", linestyle=":", alpha=0.6)

    plt.suptitle(f"Model Evaluation: {model.get_max_seq_length()} tokens", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.show()
