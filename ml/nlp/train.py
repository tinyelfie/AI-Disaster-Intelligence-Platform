"""
NLP DistilBERT Fine-Tuning

Binary classifier: disaster tweet (1) vs. not (0).
Run in Google Colab for GPU acceleration.

Usage:
    python ml/nlp/train.py

Saves:  models/nlp_model/  (HuggingFace format)
"""

import pathlib
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    get_linear_schedule_with_warmup,
)
from torch.optim import AdamW
from sklearn.metrics import f1_score

# Config
ROOT       = pathlib.Path(__file__).resolve().parents[2]
PROC_DIR   = ROOT / "data" / "processed" / "tweets"
MODEL_OUT  = ROOT / "models" / "nlp_model"
PRETRAINED = "distilbert-base-uncased"
MAX_LEN    = 128
BATCH_SIZE = 32
EPOCHS     = 4
LR         = 2e-5
DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"


# Dataset

class TweetDataset(Dataset):
    def __init__(self, csv_path: pathlib.Path, tokenizer, max_len: int):
        df = pd.read_csv(csv_path)
        self.texts  = df["clean_text"].tolist()
        self.labels = df["target"].tolist()
        self.tokenizer = tokenizer
        self.max_len   = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(),
            "attention_mask": enc["attention_mask"].squeeze(),
            "label":          torch.tensor(self.labels[idx], dtype=torch.long),
        }


# Training

def train():
    for split in ["train.csv", "val.csv"]:
        if not (PROC_DIR / split).exists():
            raise FileNotFoundError(
                f"{PROC_DIR / split} not found. Run ml/nlp/preprocess.py first."
            )

    tokenizer = DistilBertTokenizerFast.from_pretrained(PRETRAINED)
    train_ds  = TweetDataset(PROC_DIR / "train.csv", tokenizer, MAX_LEN)
    val_ds    = TweetDataset(PROC_DIR / "val.csv",   tokenizer, MAX_LEN)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=2)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

    model = DistilBertForSequenceClassification.from_pretrained(PRETRAINED, num_labels=2)
    model = model.to(DEVICE)

    optimizer = AdamW(model.parameters(), lr=LR)
    total_steps = len(train_loader) * EPOCHS
    scheduler   = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=int(0.1 * total_steps), num_training_steps=total_steps
    )

    best_f1 = 0.0

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            input_ids  = batch["input_ids"].to(DEVICE)
            attn_mask  = batch["attention_mask"].to(DEVICE)
            labels     = batch["label"].to(DEVICE)
            optimizer.zero_grad()
            out  = model(input_ids=input_ids, attention_mask=attn_mask, labels=labels)
            out.loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            total_loss += out.loss.item()

        # Validation
        model.eval()
        preds_all, labels_all = [], []
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(DEVICE)
                attn_mask = batch["attention_mask"].to(DEVICE)
                out       = model(input_ids=input_ids, attention_mask=attn_mask)
                preds_all.extend(out.logits.argmax(dim=1).cpu().tolist())
                labels_all.extend(batch["label"].tolist())

        f1 = f1_score(labels_all, preds_all)
        print(f"Epoch {epoch}/{EPOCHS}  loss={total_loss/len(train_loader):.4f}  val_f1={f1:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            MODEL_OUT.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(str(MODEL_OUT))
            tokenizer.save_pretrained(str(MODEL_OUT))
            print(f"  ✓ Saved best model (f1={f1:.4f}) to {MODEL_OUT}")

    print(f"\nTraining complete. Best val F1: {best_f1:.4f}")


if __name__ == "__main__":
    train()
