import pandas as pd

def load_category_map(path: str = "categories.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip().str.lower()
        df["keyword"] = df["keyword"].astype(str).str.lower().str.strip()
        df["category"] = df["category"].astype(str).str.lower().str.strip()
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["keyword", "category"])


def apply_category_map(df: pd.DataFrame, cat_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["category"] = "uncategorised"

    # No mappings → return df untouched
    if cat_df.empty:
        return df

    # Prepare descriptions
    desc = df["description"].astype(str).str.lower()

    # Apply keyword matching
    for _, row in cat_df.iterrows():
        key = row["keyword"]
        cat = row["category"]
        mask = desc.str.contains(key, na=False)
        df.loc[mask, "category"] = cat

    return df
