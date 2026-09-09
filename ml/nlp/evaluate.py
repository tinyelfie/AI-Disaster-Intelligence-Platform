"""
NLP Model Evaluation

F1, precision, recall per class on the test split.

Usage:
    python ml/nlp/evaluate.py
"""

import pathlib
import pandas as pd
import torch
from torch.utils.data import DataLoader
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from sklearn.metrics import classification_report
from ml.nlp.train import TweetDataset

ROOT      = pathlib.Path(__file__).resolve().parents[2]
PROC_DIR  = ROOT / "data" / "processed" / "tweets"
MODEL_OUT = ROOT / "models" / "nlp_model"
DEVICE    = "cuda" if torch.cuda.is_available() else "cpu"


def evaluate():
    if not MODEL_OUT.exists():
        print(f"[nlp.evaluate] Model not found at {MODEL_OUT}. Train first.")
        return

    tokenizer = DistilBertTokenizerFast.from_pretrained(str(MODEL_OUT))
    model     = DistilBertForSequenceClassification.from_pretrained(str(MODEL_OUT))
    model     = model.to(DEVICE)
    model.eval()

    test_ds     = TweetDataset(PROC_DIR / "test.csv", tokenizer, max_len=128)
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False)

    preds_all, labels_all = [], []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(DEVICE)
            attn_mask = batch["attention_mask"].to(DEVICE)
            out       = model(input_ids=input_ids, attention_mask=attn_mask)
            preds_all.extend(out.logits.argmax(dim=1).cpu().tolist())
            labels_all.extend(batch["label"].tolist())

    print("\n=== NLP Classification Report ===")
    print(classification_report(labels_all, preds_all,
                                target_names=["Not Disaster", "Disaster"]))


if __name__ == "__main__":
    evaluate()
