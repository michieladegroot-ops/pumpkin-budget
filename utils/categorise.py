import pandas as pd

def load_category_map(path="data/categories.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower().str.strip()
    df["keyword"] = df["keyword"].astype(str).str.lower().str.strip()
    df["category"] = df["category"].astype(str).str.lower().str.strip()
    df["parent"] = df["parent"].astype(str).str.lower().str.strip()
    return df


def apply_category_map(df: pd.DataFrame, cat_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # default values
    df["category"] = "uncategorised"
    df["parent"] = "uncategorised"

    if "merchant_key" not in df.columns:
        return df

    # convert to Series for fast lookup
    keys = cat_df["keyword"].tolist()
    cat_map = dict(zip(cat_df["keyword"], zip(cat_df["category"], cat_df["parent"])))

    for idx, key in enumerate(df["merchant_key"]):
        for kw in keys:
            if kw in key:  # substring match
                df.at[idx, "category"] = cat_map[kw][0]
                df.at[idx, "parent"] = cat_map[kw][1]
                break

    return df
