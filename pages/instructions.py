import streamlit as st

st.title('❓ Instructions')

text = """
- Use the **Upload** page to add your bank statements. You can select multiple files at once (CSV or XLSX).
- The app parses dates and amounts automatically, and stores your transactions permanently. You can close and reopen the app without losing data.
- Go to the **Dashboard** page to see summaries and your transactions. Choose a specific month or view all.
- This is version 1.0 of Pumpkin Budget, focusing on reliable ingestion and basic summaries. Categories and other features will be added in future versions.
- To deploy on Streamlit: create a GitHub repository, upload these files, then set up a new app at share.streamlit.io selecting main file `app.py` and repository name.
"""
st.markdown(text)