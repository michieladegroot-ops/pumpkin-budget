import streamlit as st
import pandas as pd
from utils.storage import get_transactions

st.title("📊 Dashboard")

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
sel = st.selectbox("Select month", month_options, index=0)

if sel == "All months":
    view = df.copy()
else:
    mid = month_table.loc[
        month_table["month_label"] == sel, "month_id"
    ].iloc[0]
    view = df[df["month_id"] == mid]

# -----------------------------
# SUMMARY METRICS
# -----------------------------
total_expense = view[view["amount"] < 0]["amount"].sum()
total_income  = view[view["amount"] > 0]["amount"].sum()
net = total_income + total_expense

col1, col2, col3 = st.columns(3)
col1.metric("Total Expenses", f"€ {abs(total_expense):,.2f}")
col2.metric("Total Income", f"€ {total_income:,.2f}")
col3.metric("Net", f"€ {net:,.2f}")

# -----------------------------
# SPENDING BY CATEGORY (EXPENSES ONLY)
# -----------------------------
st.subheader("📦 Spending by Category")

if "category" in view.columns:
    cat_totals = (
        view[view["amount"] < 0]
        .groupby("category")["amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
    )
    st.bar_chart(cat_totals)
else:
    st.info("No category data available.")

# -----------------------------
# SPENDING BY PARENT CATEGORY (EXPENSES ONLY)
# -----------------------------
st.subheader("🏷️ Spending by Parent Category")

if "parent" in view.columns:
    parent_totals = (
        view[view["amount"] < 0]
        .groupby("parent")["amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
    )
    st.bar_chart(parent_totals)
else:
    st.info("No parent category data available.")

# -----------------------------
# CATEGORY TABLE (EXPENSES ONLY)
# -----------------------------
st.subheader("🥧 Category Distribution (Spending)")

if "category" in view.columns:
    pie_data = (
        view[view["amount"] < 0]
        .groupby("category")["amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
    )
    st.dataframe(pie_data)
else:
    st.info("No category data to show.")

# -----------------------------
# TREND OVER TIME (ALL MONTHS)
# -----------------------------
st.subheader("📈 Net Cashflow Over Time (All Months)")

trend = (
    df.groupby("month_label")["amount"]
    .sum()
    .reindex(month_table["month_label"])
    .fillna(0)
)

st.line_chart(trend)

# -----------------------------
# INCOME VS EXPENSES OVER TIME (ALL MONTHS)
# -----------------------------
st.subheader("💶 Income vs Expenses Over Time")

trend_income = (
    df[df["amount"] > 0]
    .groupby("month_label")["amount"]
    .sum()
    .reindex(month_table["month_label"])
    .fillna(0)
)

trend_expense = (
    df[df["amount"] < 0]
    .groupby("month_label")["amount"]
    .sum()
    .abs()
    .reindex(month_table["month_label"])
    .fillna(0)
)

st.area_chart(
    pd.DataFrame({
        "Income": trend_income,
        "Expenses": trend_expense
    })
)

# -----------------------------
# TRANSACTION TABLE
# -----------------------------
st.subheader("📄 Transactions")
st.dataframe(view)
