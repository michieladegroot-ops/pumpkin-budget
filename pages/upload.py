import streamlit as st
import pandas as pd

from utils.ingest import clean_bank_data
from utils.storage import append_transactions, get_transactions
from utils.categorise import load_category_map, apply_category_map

st.title('📥 Upload Statement')
st.write('Upload your bank statement files (.csv or .xlsx). They will be parsed, categorised, and stored.')

uploaded_files = st.file_uploader(
    "Choose one or more files",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

if uploaded_files:
    total_new = 0

    # Load your category mapping file once
    cat_df = load_category_map("data/categories.csv")

    for uploaded_file in uploaded_files:
        try:
            # READ ---------------------------------------------------------
            if uploaded_file.name.lower().endswith("xlsx"):
                df_raw = pd.read_excel(uploaded_file)
            else:
                df_raw = pd.read_csv(uploaded_file)

            # CLEAN --------------------------------------------------------
            df = clean_bank_data(df_raw)

            # CATEGORISE ---------------------------------------------------
            df = apply_category_map(df, cat_df)

            # STORE --------------------------------------------------------
            append_transactions(df)
            total_new += len(df)

        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e!s}")
            continue

    st.success(f"Successfully added {total_new} transactions.")
    st.write("You now have", len(get_transactions()), "transaction(s) in total.")
