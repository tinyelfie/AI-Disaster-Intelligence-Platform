"""
NLP Tweet Preprocessing

Cleans disaster tweets, tokenizes for DistilBERT fine-tuning.

Usage:
    python ml/nlp/preprocess.py
"""

import re
import pathlib
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT     = pathlib.Path(__file__).resolve().parents[2]
RAW_CSV  = ROOT / "data" / "raw" / "tweets" / "disaster_tweets.csv"
PROC_DIR = ROOT / "data" / "processed" / "tweets"


def clean_text(text: str) -> str:
    """Remove URLs, @mentions, #hashtags, special chars. Lowercase."""
    text = re.sub(r"http\S+|www\S+", "", text)              # URLs
    text = re.sub(r"@\w+", "", text)                         # Mentions
    text = re.sub(r"#(\w+)", r"\1", text)                    # Hashtags → word
    text = re.sub(r"[^\w\s.,!?'-]", " ", text)              # Special chars
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def preprocess():
    if not RAW_CSV.exists():
        print(f"[nlp.preprocess] {RAW_CSV} not found. "
              "Download disaster_tweets.csv from Kaggle first.")
        return

    df = pd.read_csv(RAW_CSV)

    # Expected columns: id, keyword, location, text, target
    required = {"text", "target"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required}. Found: {df.columns.tolist()}")

    df["clean_text"] = df["text"].astype(str).apply(clean_text)
    df = df.dropna(subset=["clean_text", "target"])
    df["target"] = df["target"].astype(int)

    # 80/10/10 split
    train, temp = train_test_split(df, test_size=0.2, random_state=42, stratify=df["target"])
    val, test   = train_test_split(temp, test_size=0.5, random_state=42, stratify=temp["target"])

    PROC_DIR.mkdir(parents=True, exist_ok=True)
    train[["clean_text", "target"]].to_csv(PROC_DIR / "train.csv", index=False)
    val[["clean_text", "target"]].to_csv(PROC_DIR / "val.csv",   index=False)
    test[["clean_text", "target"]].to_csv(PROC_DIR / "test.csv",  index=False)

    print(f"[nlp.preprocess] Done.  train={len(train)}  val={len(val)}  test={len(test)}")
    print(f"  Label distribution (train):\n{train['target'].value_counts()}")


if __name__ == "__main__":
    preprocess()
