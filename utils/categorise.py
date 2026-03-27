import pandas as pd

def load_category_map(path: str = "data/categories.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip().str.lower()

        # Ensure missing columns exist
        if "parent" not in df.columns:
            df["parent"] = "other"

        df["keyword"] = df["keyword"].astype(str).str.lower().str.strip()
        df["category"] = df["category"].astype(str).str.lower().str.strip()
        df["parent"] = df["parent"].astype(str).str.lower().str.strip()

        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["keyword", "category", "parent"])


def apply_category_map(df: pd.DataFrame, cat_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["category"] = "uncategorised"
    df["parent"] = "uncategorised"

    if cat_df.empty:
        return df

    desc = df["description"].astype(str).str.lower()

    for _, row in cat_df.iterrows():
        key = row["keyword"]
        cat = row["category"]
        parent = row["parent"]

        mask = desc.str.contains(key, na=False)
        df.loc[mask, "category"] = cat
        df.loc[mask, "parent"] = parent

    return df
