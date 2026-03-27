import pandas as pd
from pathlib import Path

# Persistent storage for transactions. Uses a CSV in the data folder.
FILEPATH = Path(__file__).parent.parent.joinpath("data", "transactions.csv")

# Define the canonical columns
CANONICAL_COLS = ["date","amount","amount_abs","description","year","month_id","month_label"]

def get_transactions() -> pd.DataFrame:
    """Read the transactions from the persistent CSV. If missing, return an empty DataFrame."""
    if not FILEPATH.exists():
        return pd.DataFrame(columns=CANONICAL_COLS)
    df = pd.read_csv(FILEPATH, parse_dates=["date"])
    for col in CANONICAL_COLS:
        if col not in df.columns:
            df[col] = pd.NA
    return df

def save_transactions(df: pd.DataFrame) -> None:
    """Save transactions to the persistent CSV."""
    FILEPATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(FILEPATH, index=False)

def append_transactions(new_df: pd.DataFrame) -> None:
    """Append new transactions to the CSV, avoiding duplicates."""
    df = get_transactions()
    combined = pd.concat([df, new_df], ignore_index=True)
    combined = combined.drop_duplicates()
    save_transactions(combined)