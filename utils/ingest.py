import pandas as pd

# Clean imported bank data and unify the schema
# Detects date, amount, description columns by common patterns, and returns a DataFrame with canonical fields.

def clean_bank_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Normalize column names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    # Detect date column
    date_candidates = [c for c in df.columns if "date" in c or "datum" in c]
    if not date_candidates:
        raise ValueError("No date column found in uploaded file.")
    date_col = date_candidates[0]
    df["date"] = pd.to_datetime(df[date_col], errors="coerce")
    df = df[df["date"].notna()].reset_index(drop=True)
    # Detect amount column
    amount_candidates = [c for c in df.columns if "amount" in c or "bedrag" in c]
    if not amount_candidates:
        raise ValueError("No amount column found in uploaded file.")
    amount_col = amount_candidates[0]
    df["amount"] = pd.to_numeric(df[amount_col], errors="coerce")
    df["amount_abs"] = df["amount"].abs()
    # Detect description column
    desc_candidates = [c for c in df.columns if "description" in c or "omschrijving" in c or "name" in c]
    if desc_candidates:
        df["description"] = df[desc_candidates[0]].astype(str).str.strip()
    else:
        df["description"] = ""
    # Create canonical time fields
    df["year"] = df["date"].dt.year
    df["month_id"] = df["date"].dt.strftime("%Y-%m")
    df["month_label"] = df["date"].dt.strftime("%b %Y")
    return df