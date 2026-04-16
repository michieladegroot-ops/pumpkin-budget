import streamlit as st
import pandas as pd
from utils.storage import get_transactions

st.title("📊 Dashboard")

# -----------------------------
# LOAD DATA
# -----------------------------
df = get_transactions()
if df is None or df.empty:
    st.info("No transactions yet. Upload one or more files on the Upload page.")
    st.stop()

# Ensure date is datetime
if not pd.api.types.is_datetime64_any_dtype(df["date"]):
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["date"].notna()]

# -----------------------------
# MONTH SELECTION
# -----------------------------
month_table = (
    df[["month_id", "month_label"]]
    .drop_duplicates()
    .sort_values("month_id")
)

month_options = ["All months"] + month_table["month_label"].tolist()
selected_month = st.selectbox("Select month", month_options, index=0)

if selected_month == "All months":
    view = df.copy()
else:
    mid = month_table.loc[
        month_table["month_label"] == selected_month,
        "month_id"
    ].iloc[0]
    view = df[df["month_id"] == mid]

# -----------------------------
# SUMMARY METRICS
# -----------------------------
total_expense = view[view["amount"] < 0]["amount"].sum()
total_income = view[view["amount"] > 0]["amount"].sum()
net = total_income + total_expense

col1, col2, col3 = st.columns(3)
col1.metric("Total Expenses", f"€ {abs(total_expense):,.0f}")
col2.metric("Total Income", f"€ {total_income:,.0f}")
col3.metric("Net", f"€ {net:,.0f}")

# -----------------------------
# ANALYSIS CONTROLS
# -----------------------------
st.subheader("Analysis controls")

sort_order = st.selectbox(
    "Sort expenses",
    ["Highest → Lowest", "Lowest → Highest"]
)

exclude_categories = st.multiselect(
    "Exclude categories from analysis",
    sorted(view["category"].unique())
)

ascending = sort_order == "Lowest → Highest"

# Apply exclusions
analysis_view = view[
    (view["amount"] < 0) &
    (~view["category"].isin(exclude_categories))
].copy()

# -----------------------------
# SPENDING BY CATEGORY
# -----------------------------
st.subheader("📦 Spending by Category")

cat_totals = (
    analysis_view
    .groupby("category")["amount"]
    .sum()
    .abs()
    .sort_values(ascending=ascending)
)

st.bar_chart(cat_totals)

cat_table = cat_totals.reset_index()
cat_table.columns = ["Category", "Amount (€)"]
cat_table["Amount (€)"] = cat_table["Amount (€)"].apply(
    lambda x: f"€ {x:,.0f}"
)

st.dataframe(cat_table, hide_index=True)

# -----------------------------
# SPENDING BY PARENT CATEGORY
# -----------------------------
st.subheader("🏷️ Spending by Parent Category")

parent_totals = (
    analysis_view
    .groupby("parent")["amount"]
    .sum()
    .abs()
    .sort_values(ascending=ascending)
)

st.bar_chart(parent_totals)

parent_table = parent_totals.reset_index()
parent_table.columns = ["Parent category", "Amount (€)"]
parent_table["Amount (€)"] = parent_table["Amount (€)"].apply(
    lambda x: f"€ {x:,.0f}"
)

st.dataframe(parent_table, hide_index=True)

# -----------------------------
# TRANSACTIONS TABLE
# -----------------------------
st.subheader("📄 Transactions")

tx_table = analysis_view.copy()
tx_table["amount"] = tx_table["amount"].apply(lambda x: f"€ {abs(x):,.0f}")

st.dataframe(
    tx_table[[
        "date",
        "description",
        "category",
        "parent",
        "amount"
    ]],
    hide_index=True
)
