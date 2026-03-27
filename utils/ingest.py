import pandas as pd
import re

def extract_merchant_key(description: str) -> str:
    """
    Extract clean, stable merchant key using the SAME rules
    used to generate master_categories_new.csv.
    """

    text = str(description).lower()

    # 1. Google Pay pattern
    if "google pay" in text:
        after = text.split("google pay", 1)[1]
        after = after.split(",", 1)[0].strip()
        cleaned = re.sub(r"[^a-z0-9 &]", " ", after)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if cleaned:
            return cleaned

    # 2. /NAME/ pattern
    if "/name/" in text:
        after = text.split("/name/", 1)[1].split("/", 1)[0].strip()
        cleaned = re.sub(r"[^a-z0-9 &]", " ", after)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if cleaned:
            return cleaned

    # 3. fallback — cleaned full description
    cleaned = re.sub(r"[^a-z0-9 &]", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def clean_bank_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # normalize headers
    df.columns = (
        df.columns.astype(str)
        .str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # date parsing
    if "transactiondate" in df.columns:
        df["date"] = pd.to_datetime(
            df["transactiondate"].astype(str),
            format="%Y%m%d",
            errors="coerce",
        )
    elif "valuedate" in df.columns:
        df["date"] = pd.to_datetime(
            df["valuedate"].astype(str),
            format="%Y%m%d",
            errors="coerce",
        )
    df = df[df["date"].notna()].reset_index(drop=True)

    # amounts
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["amount_abs"] = df["amount"].abs()

    # description
    df["description"] = df["description"].astype(str).fillna("")

    # NEW: merchant key extraction
    df["merchant_key"] = df["description"].apply(extract_merchant_key)

    # time fields
    df["year"] = df["date"].dt.year
    df["month_id"] = df["date"].dt.strftime("%Y-%m")
    df["month_label"] = df["date"].dt.strftime("%b %Y")

    return df
