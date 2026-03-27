# Pumpkin Budget

Pumpkin Budget is a personal finance tracker for simple and reliable ingestion of bank statements and basic summaries. This is version 1.0 focusing on stability.

## Usage

- Use the **Upload** page to add your bank statements. You can select multiple files at once (CSV or XLSX). The files are parsed and stored permanently in `data/transactions.csv`.
- Go to the **Dashboard** page to see summaries (total expenses, total income, net) and a bar chart of money flow over time. Choose a specific month or view all.
- The **Instructions** page reminds you how to use the app.

## Deployment

1. Create a new GitHub repository called `pumpkin-budget` (or another name of your choice) with no README or .gitignore.
2. Upload all files from this project into the repository. The root of the repository should contain `app.py`, the `pages/` folder, `utils/` folder, `data/` folder, and `requirements.txt`.
3. On Streamlit Cloud (https://share.streamlit.io), click **New app**, select your repository and branch (usually `main`), set Main file to `app.py`, and click **Deploy**.
4. Once deployed, the app will be available at `https://<your-username>-pumpkin-budget.streamlit.app` or similar.

## Local development

You can run the app locally if you have Python installed. Install dependencies:

```
pip install -r requirements.txt
```

Then run:

```
streamlit run app.py
```
