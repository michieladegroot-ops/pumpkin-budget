import streamlit as st
import pandas as pd
from utils.storage import get_transactions

st.title('📊 Dashboard')

df = get_transactions()
if df is None or df.empty:
    st.info("No transactions yet. Upload one or more files on the Upload page.")
    st.stop()
if not pd.api.types.is_datetime64_any_dtype(df["date"]):
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["date"].notna()]

month_table = (
    df[["month_id","month_label"]].drop_duplicates().sort_values("month_id")
)
month_options = ["All months"] + month_table["month_label"].tolist()
sel = st.selectbox("Select month", month_options, index=0)

if sel == "All months":
    view = df.copy()
else:
    mid = month_table.loc[month_table["month_label"] == sel, "month_id"].iloc[0]
    view = df[df["month_id"] == mid]

total_expense = view[view["amount"] < 0]["amount"].sum()
total_income  = view[view["amount"] > 0]["amount"].sum()
net = total_income + total_expense

col1, col2, col3 = st.columns(3)
col1.metric("Total Expenses", f"€ {abs(total_expense):,.2f}")
col2.metric("Total Income", f"€ {total_income:,.2f}")
col3.metric("Net", f"€ {net:,.2f}")

st.subheader("Spending & Income Over Time")
expense_by_month = df.groupby("month_label")["amount"].sum().reindex(month_table["month_label"]).fillna(0)
st.bar_chart(expense_by_month)

st.subheader("Transactions")
st.dataframe(view)
