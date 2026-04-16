import streamlit as st
import pandas as pd
from utils.storage import get_transactions

st.title("📈 Insights")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
df = get_transactions()
if df is None or df.empty:
    st.info("No transactions available.")
    st.stop()

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df[df["date"].notna()]

# Only expenses
df_exp = df[df["amount"] < 0].copy()
df_exp["spend"] = df_exp["amount"].abs()

# -------------------------------------------------
# SELECT CATEGORY
# -------------------------------------------------
categories = sorted(df_exp["category"].unique())
category = st.selectbox("Select category", categories)

cat_df = df_exp[df_exp["category"] == category].copy()

if cat_df.empty:
    st.info("No expenses for this category.")
    st.stop()

# -------------------------------------------------
# SELECT MONTH
# -------------------------------------------------
months = (
    cat_df[["month_id", "month_label"]]
    .drop_duplicates()
    .sort_values("month_id")
    .reset_index(drop=True)
)

month_labels = months["month_label"].tolist()
selected_month = st.selectbox(
    "Select month",
    month_labels,
    index=len(month_labels) - 1
)

current_pos = months.index[
    months["month_label"] == selected_month
][0]

if current_pos == 0:
    st.info("No previous month available for comparison.")
    st.stop()

current_month_id = months.loc[current_pos, "month_id"]
prev_month_id = months.loc[current_pos - 1, "month_id"]
prev_month_label = months.loc[current_pos - 1, "month_label"]


# -------------------------------------------------
# AGGREGATION
# -------------------------------------------------
cur = cat_df[cat_df["month_id"] == current_month_id]
prev = cat_df[cat_df["month_id"] == prev_month_id]

cur_total = cur["spend"].sum()
prev_total = prev["spend"].sum()

delta = cur_total - prev_total
pct = (delta / prev_total * 100) if prev_total > 0 else None

# -------------------------------------------------
# SUMMARY
# -------------------------------------------------
st.subheader("Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    f"{selected_month}",
    f"€ {cur_total:,.0f}"
)

col2.metric(
    f"{prev_month_label}",
    f"€ {prev_total:,.0f}"
)

delta_label = f"€ {delta:,.0f}"
pct_label = f"{pct:+.0f}%" if pct is not None else "—"

col3.metric(
    "Change",
    delta_label,
    pct_label
)

# -------------------------------------------------
# NARRATIVE
# -------------------------------------------------
st.subheader("What changed?")

if delta > 0:
    st.write(
        f"Spending on **{category}** increased by "
        f"€ {delta:,.0f} (+{pct:.0f}%) compared to {prev_month_label}."
    )
elif delta < 0:
    st.write(
        f"Spending on **{category}** decreased by "
        f"€ {abs(delta):,.0f} ({pct:.0f}%) compared to {prev_month_label}."
    )
else:
    st.write(
        f"Spending on **{category}** was unchanged compared to {prev_month_label}."
    )

# -------------------------------------------------
# DRIVERS
# -------------------------------------------------
st.subheader("Key drivers")

drivers = (
    cur.groupby("description")["spend"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

drivers["spend"] = drivers["spend"].apply(lambda x: f"€ {x:,.0f}")

st.dataframe(
    drivers.rename(columns={
        "description": "Transaction",
        "spend": "Amount"
    }),
    hide_index=True
)

# -------------------------------------------------
# CONTEXT TABLE
# -------------------------------------------------
with st.expander("See all transactions for this category and month"):
    table = cur.copy()
    table["amount"] = table["spend"].apply(lambda x: f"€ {x:,.0f}")

    st.dataframe(
        table[["date", "description", "amount"]],
        hide_index=True
    )
