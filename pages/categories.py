import streamlit as st
import pandas as pd
from utils.categorise import load_category_map

st.title("📚 Manage Categories")

# Load the category mapping file
cat_df = load_category_map("data/categories.csv")

st.subheader("Current keyword → category mappings")
st.dataframe(cat_df)

st.write("---")

# --- ADD NEW MAPPING ---------------------------------------------------
st.subheader("➕ Add New Mapping")

new_keyword = st.text_input("Keyword (text to search for in description)")
new_category = st.text_input("Category name")

if st.button("Add mapping"):
    if new_keyword.strip() == "" or new_category.strip() == "":
        st.error("Both keyword and category must be filled in.")
    else:
        # Append row
        new_row = {
            "keyword": new_keyword.lower().strip(),
            "category": new_category.lower().strip()
        }
        cat_df = pd.concat([cat_df, pd.DataFrame([new_row])], ignore_index=True)
        cat_df.to_csv("data/categories.csv", index=False)
        st.success("Mapping added. Refresh the page to see it.")

st.write("---")

# --- DELETE / EDIT MAPPINGS --------------------------------------------
st.subheader("🗑️ Delete Existing Mapping")

if len(cat_df) == 0:
    st.info("No mappings available.")
else:
    keyword_list = cat_df["keyword"].tolist()
    to_delete = st.selectbox("Select keyword to delete", [""] + keyword_list)

    if st.button("Delete mapping"):
        if to_delete == "":
            st.error("Choose a keyword first.")
        else:
            cat_df = cat_df[cat_df["keyword"] != to_delete]
            cat_df.to_csv("data/categories.csv", index=False)
            st.success(f"Mapping for '{to_delete}' deleted. Refresh the page to see changes.")
