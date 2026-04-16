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
# MONTHS
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

current_pos = months.index[months["month_label"] == selected_month][0]
current_month_id = months.loc[current_pos, "month_id"]

# -------------------------------------------------
# BASELINE WINDOW
# -------------------------------------------------
baseline_window = st.selectbox(
    "Compare against average of previous",
    ["2 months", "3 months", "6 months"],
    index=1
)
window = int(baseline_window.split()[0])

if current_pos == 0:
    st.info("Not enough history for comparison.")
    st.stop()

baseline_start = max(0, current_pos - window)
baseline_months = months.loc[baseline_start:current_pos - 1, "month_id"]

# -------------------------------------------------
# AGGREGATION
# -------------------------------------------------
cur = cat_df[cat_df["month_id"] == current_month_id]
baseline = cat_df[cat_df["month_id"].isin(baseline_months)]

cur_total = cur["spend"].sum()
baseline_avg = baseline.groupby("month_id")["spend"].sum().mean()

delta = cur_total - baseline_avg
pct = (delta / baseline_avg * 100) if baseline_avg > 0 else None

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
    f"{baseline_window} average",
    f"€ {baseline_avg:,.0f}"
)

pct_label = f"{pct:+.0f}%" if pct is not None else "—"
col3.metric(
    "Difference",
    f"€ {delta:,.0f}",
    pct_label
)

# -------------------------------------------------
# TREND CHART
# -------------------------------------------------
st.subheader("Monthly trend")

trend = (
    cat_df
    .groupby("month_label")["spend"]
    .sum()
    .reindex(months["month_label"])
)

st.line_chart(trend)

# -------------------------------------------------
# NARRATIVE
# -------------------------------------------------
st.subheader("What does this mean?")

if delta > 0:
    st.write(
        f"Spending on **{category}** in **{selected_month}** was "
        f"€ {delta:,.0f} higher than the {baseline_window} average "
        f"(+{pct:.0f}%)."
    )
elif delta < 0:
    st.write(
        f"Spending on **{category}** in **{selected_month}** was "
        f"€ {abs(delta):,.0f} lower than the {baseline_window} average "
        f"({pct:.0f}%)."
    )
else:
    st.write(
        f"Spending on **{category}** was in line with the recent average."
    )

# -------------------------------------------------
# DRIVERS
# -------------------------------------------------
st.subheader("Key drivers this month")

drivers = (
    cur.groupby("description")["spend"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

drivers["share"] = drivers["spend"] / cur_total
drivers["spend"] = drivers["spend"].apply(lambda x: f"€ {x:,.0f}")
drivers["share"] = drivers["share"].apply(lambda x: f"{x:.0%}")

st.dataframe(
    drivers.rename(columns={
        "description": "Transaction",
        "spend": "Amount",
        "share": "Share of month"
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
