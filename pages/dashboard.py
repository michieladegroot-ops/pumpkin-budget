import streamlit as st
import pandas as pd
from utils.storage import get_transactions

st.title('📊 Dashboard')

df = get_transactions()
if df is None or df.empty:
    st.info("No transactions yet. Upload one or more files on the Upload page.")
    st.stop()

# Ensure date is datetime
if not pd.api.types.is_datetime64_any_dtype(df["date"]):
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["date"].notna()]

# Build month list
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
    mid = month_table.loc[month_table["month_label"] == sel, "month_id"].iloc[0]
    view = df[df["month_id"] == mid]

# SUMMARY -----------------------------------------------------
total_expense = view[view["amount"] < 0]["amount"].sum()
total_income  = view[view["amount"] > 0]["amount"].sum()
net = total_income + total_expense

col1, col2, col3 = st.columns(3)
col1.metric("Total Expenses", f"€ {abs(total_expense):,.2f}")
col2.metric("Total Income", f"€ {total_income:,.2f}")
col3.metric("Net", f"€ {net:,.2f}")

# CATEGORY BAR CHART -----------------------------------------
st.subheader("📦 Spending by Category")

if "category" in view.columns:
    cat_totals = (
        view.groupby("category")["amount_abs"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(cat_totals)
else:
    st.info("No categories available. Upload a file to generate categories.")

# PARENT CATEGORY CHART -------------------------------------------------
st.subheader("🏷️ Spending by Parent Category")

if "parent" in view.columns:
    parent_totals = (
        view.groupby("parent")["amount_abs"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(parent_totals)
else:
    st.info("No parent category data available.")

# CATEGORY PIE CHART -----------------------------------------
st.subheader("🥧 Category Distribution (Spending)")

if "category" in view.columns and not view.empty:
    pie_data = (
        view[view["amount"] < 0]
        .groupby("category")["amount_abs"]
        .sum()
        .reset_index()
    )

    # Streamlit's built-in pie chart alternative:
    st.dataframe(pie_data.set_index("category"))
    st.caption("(*Pie chart libraries require Plotly or Altair — can add later if you want.*)")
else:
    st.info("No category data to show.")

# TREND LINE --------------------------------------------------
st.subheader("📈 Spending Trend Over Time (All Months)")

trend = (
    df.groupby("month_label")["amount"]
    .sum()
    .reindex(month_table["month_label"])
    .fillna(0)
)

st.line_chart(trend)

# INCOME VS EXPENSES -----------------------------------------
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
    .reindex(month_table["month_label"])
    .fillna(0)
)

st.area_chart(
    pd.DataFrame({
        "Income": trend_income,
        "Expenses": trend_expense.abs()
    })
)

# TRANSACTION TABLE -------------------------------------------
st.subheader("📄 Transactions")
st.dataframe(view)
