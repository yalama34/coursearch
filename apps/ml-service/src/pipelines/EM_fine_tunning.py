import torch
from torch.utils.data import DataLoader, WeightedRandomSampler
from sentence_transformers import SentenceTransformer, losses

from pathlib import Path

from .synthetic_data_cleaner_pipeline import get_data_for_pipeline
from .model_evaluation import ExtendedMetricsEvaluator, evaluate_and_plot


OUT = Path(__file__).resolve().parent.parent.parent / "models" / "course-emb-v1"
OUT.mkdir(parents=True, exist_ok=True)

EPSILON = 0.01
EPOCHS = 8
BATCH_SIZE = 32
LR = 2e-5

train_examples, val_examples, df_test = get_data_for_pipeline()

val_sentences1 = [ex.texts[0] for ex in val_examples]
val_sentences2 = [ex.texts[1] for ex in val_examples]
val_scores = [float(ex.label) for ex in val_examples]

static_val_evaluator = ExtendedMetricsEvaluator(
    sentences1=val_sentences1,
    sentences2=val_sentences2,
    scores=val_scores,
    batch_size=16,
    name="static-validation",
    show_progress_bar=True,
    write_csv=True
)

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
train_loss = losses.CosineSimilarityLoss(model=model)
train_dataloader = DataLoader(train_examples, batch_size=BATCH_SIZE, shuffle=True)

def fine_tune() -> None:
    """
    Executes the fine-tuning process for the SentenceTransformer model.
    """
    global train_dataloader
    for epoch in range(EPOCHS):
        model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=1,
            warmup_steps=int(len(train_dataloader) / BATCH_SIZE * 0.1),
            show_progress_bar=False,
            scheduler="WarmupCosine",
            evaluator=static_val_evaluator,
            evaluation_steps=40,
            output_path=str(OUT),
            save_best_model=True,
            optimizer_params={"lr": LR, "weight_decay": 0.01}
        )

        sentences1 = [ex.texts[0] for ex in train_examples]
        sentences2 = [ex.texts[1] for ex in train_examples]
        labels = torch.tensor([ex.label for ex in train_examples], dtype=torch.float32)

        model.eval()
        with torch.no_grad():
            emb1 = model.encode(sentences1, convert_to_tensor=True)
            emb2 = model.encode(sentences2, convert_to_tensor=True)
            predictions = torch.nn.functional.cosine_similarity(emb1, emb2)

        errors = torch.abs(labels - predictions.cpu())
        weights = torch.pow(errors, 2) + EPSILON
        sampler = WeightedRandomSampler(
            weights=weights,
            num_samples=len(train_examples),
            replacement=True
        )

        train_dataloader = DataLoader(
            train_examples,
            batch_size=BATCH_SIZE,
            sampler=sampler
        )
        model.train()

        print(f"Epoch {epoch + 1} complete. Mean training error: {errors.mean():.4f}")
        model.save(str(OUT))

if __name__ == "__main__":
    fine_tune()
    model = SentenceTransformer(str(OUT))
    evaluate_and_plot(model, df_test, 32)
