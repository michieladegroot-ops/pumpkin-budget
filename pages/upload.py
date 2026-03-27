import streamlit as st
import pandas as pd
from utils.ingest import clean_bank_data
from utils.storage import append_transactions, get_transactions

st.title('📥 Upload Statement')
st.write('Upload your bank statement files (.csv or .xlsx). They will be parsed and stored persistently.')

uploaded_files = st.file_uploader("Choose one or more files", type=["csv","xlsx"], accept_multiple_files=True)
if uploaded_files:
    total_new = 0
    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.name.lower().endswith("xlsx"):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
            df = clean_bank_data(df)
            append_transactions(df)
            total_new += len(df)
        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e!s}")
            continue
    st.success(f"Successfully added {total_new} transactions.")
    st.write("You now have", len(get_transactions()), "transaction(s) in total.")