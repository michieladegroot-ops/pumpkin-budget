import streamlit as st
import pandas as pd

st.title("🎃 Pumpkin Budget — Fresh Start")

uploaded = st.file_uploader("Upload ABN Bank Statement (.xlsx)", type="xlsx")

if uploaded:
    # Read Excel
    df = pd.read_excel(uploaded)

    # --- CLEANING -------------------------------------------------------
    # Parse correct date format (YYYYMMDD → real date)
    df["date"] = pd.to_datetime(
        df["transactiondate"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # Derive month for filtering
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # Ensure text column safe
    df["description"] = df["description"].astype(str).fillna("")

    # Absolute amount for charts
    df["amount_abs"] = df["amount"].abs()

    # --- CATEGORISATION -------------------------------------------------
    try:
        cat_df = pd.read_csv("categories.csv")
        cat_df["keyword"] = cat_df["keyword"].str.lower().str.strip()
        cat_df["category"] = cat_df["category"].str.lower().str.strip()

        df["category"] = "uncategorised"
        descriptions = df["description"].str.lower()

        for _, row in cat_df.iterrows():
            key = row["keyword"]
            cat = row["category"]
            mask = descriptions.str.contains(key, na=False)
            df.loc[mask, "category"] = cat

    except FileNotFoundError:
        st.warning("No categories.csv found — all transactions will be uncategorised.")
        df["category"] = "uncategorised"

    # --- PREVIEW --------------------------------------------------------
    st.subheader("Preview of uploaded data")
    st.dataframe(df.head())

    # --- MONTH FILTER ---------------------------------------------------
    months = sorted(df["month"].unique())
    sel_month = st.selectbox("Select Month", months)

    df_month = df[df["month"] == sel_month]

    # --- SUMMARY --------------------------------------------------------
    st.subheader(f"Summary for {sel_month}")

    total_spending = abs(df_month[df_month.amount < 0]["amount"].sum())
    total_income = df_month[df_month.amount > 0]["amount"].sum()

    st.metric("Total Spending", f"€ {total_spending:,.2f}")
    st.metric("Total Income", f"€ {total_income:,.2f}")

    # --- CATEGORY SUMMARY ----------------------------------------------
    st.subheader("Category Breakdown")
    st.write(df_month["category"].value_counts())

    st.subheader("Uncategorised Transactions")
    st.dataframe(df_month[df_month["category"] == "uncategorised"])

    # --- TRANSACTIONS ---------------------------------------------------
    st.subheader("All Transactions")
    st.dataframe(df_month)
