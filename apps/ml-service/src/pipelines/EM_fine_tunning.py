from pathlib import Path
from collections.abc import Iterable

import torch
from torch.types import Tensor
from torch.utils.data import DataLoader, WeightedRandomSampler
from sentence_transformers import SentenceTransformer, losses

from .synthetic_data_cleaner_pipeline import get_data_for_pipeline
from .model_evaluation import ExtendedMetricsEvaluator, evaluate_and_plot


OUT = Path(__file__).resolve().parent.parent.parent / "models" / "course-emb-v1.1"
OUT.mkdir(parents=True, exist_ok=True)

EPSILON = 0.001
EPOCHS = 12
BATCH_SIZE = 32
LR = 1e-5

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
train_dataloader = DataLoader(train_examples, batch_size=BATCH_SIZE, shuffle=True)

class CustomMSELoss(torch.nn.Module):
    def __init__(
        self,
        model: SentenceTransformer,
        power_weight: float = 2.0,
        power: int = 2,
        max_err_weight: float = 1.0,
        loss_fct: torch.nn.Module = torch.nn.MSELoss()):
        super().__init__()
        self.model = model
        self.loss_fct = loss_fct
        self.power_weight = power_weight
        self.power = power
        self.max_err_weight = max_err_weight

    def forward(self, sentence_features, labels: Iterable[dict[str, Tensor]]):
        embeddings = [self.model(sentence_feature)["sentence_embedding"] for sentence_feature in sentence_features]

        predictions = torch.clamp(torch.cosine_similarity(embeddings[0], embeddings[1]), min=0.0, max=1.0)

        labels = labels.view(-1)

        base_loss = self.loss_fct(predictions, labels)

        errors = torch.abs(predictions - labels)
        top_errors = torch.topk(errors, k=min(20, errors.size(0))).values
        max_err_penalty = torch.mean(torch.pow(top_errors, 2))

        penalty = torch.mean(torch.pow(errors, self.power))

        total_loss = base_loss + (self.power_weight * penalty) + (self.max_err_weight * max_err_penalty)

        return total_loss

train_loss = CustomMSELoss(model=model, power_weight=2.0, power=2, max_err_weight=1.0)

def fine_tune() -> None:
    """
    Executes the fine-tuning process for the SentenceTransformer model.
    """
    global train_dataloader
    for epoch in range(EPOCHS):
        model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=1,
            warmup_steps=int(len(train_dataloader) * 0.1),
            show_progress_bar=True,
            evaluation_steps=40,
            scheduler="WarmupCosine",
            evaluator=static_val_evaluator,
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
