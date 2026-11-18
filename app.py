import os
import json
import re
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from google import genai

st.set_page_config(page_title="Smart Expense Categorizer", page_icon="💸", layout="wide")

CATEGORIES = ["Food", "Travel", "Bills", "Shopping", "Healthcare", "Education", "Entertainment", "Rent", "Groceries", "Other"]

st.title("💸 Smart Expense Categorizer")
st.write("Upload your bank transactions and let GenAI organize your spending.")
st.info("Demo project: use sample or anonymized transactions. Do not upload real banking details or account numbers.")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API key", type="password", help="Get a key from Google AI Studio.")
    model_name = st.text_input("Gemini model", value="gemini-3.8-flash")
    st.caption("Your API key is used only while this app is running. Never upload it to GitHub.")

uploaded = st.file_uploader("Upload transactions CSV", type=["csv"])
st.caption("Required columns: date, description, amount")

def categorize_with_gemini(df, key, model):
    client = genai.Client(api_key=key)
    rows = df[["date", "description", "amount"]].fillna("").to_dict(orient="records")
    prompt = f"""
You are an expense categorization assistant. Categorize every transaction into exactly one of:
{", ".join(CATEGORIES)}.
Return ONLY a valid JSON array. Each object must contain:
- index: the zero-based row index from the input
- category: one category from the allowed list
- reason: a short reason (maximum 12 words)
Do not change transaction amounts or dates. If unclear, use Other.

Transactions:
{json.dumps(rows, default=str)}
"""
    response = client.models.generate_content(model=model, contents=prompt)
    raw = response.text or ""
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.I)
    match = re.search(r"\[[\s\S]*\]", raw)
    if not match:
        raise ValueError("The AI did not return a valid JSON array. Please try again.")
    result = json.loads(match.group(0))
    mapping = {}
    for item in result:
        idx = int(item["index"])
        category = item["category"]
        if category not in CATEGORIES:
            category = "Other"
        mapping[idx] = (category, str(item.get("reason", "")))
    return mapping

if uploaded:
    try:
        data = pd.read_csv(uploaded)
        required = {"date", "description", "amount"}
        if not required.issubset(set(data.columns.str.lower())):
            st.error("CSV must contain columns named: date, description, amount.")
            st.stop()
        data.columns = [c.strip().lower() for c in data.columns]
        data["amount"] = pd.to_numeric(data["amount"], errors="coerce")
        data = data.dropna(subset=["amount"]).copy()
        data["date"] = pd.to_datetime(data["date"], errors="coerce")
        data = data.dropna(subset=["date"]).copy()
        data["description"] = data["description"].fillna("").astype(str)
        if data.empty:
            st.warning("No valid transactions found in this CSV.")
            st.stop()

        st.subheader("1. Preview transactions")
        st.dataframe(data, use_container_width=True)

        if st.button("✨ Categorize expenses with GenAI", type="primary"):
            if not api_key:
                st.error("Enter your Gemini API key in the sidebar first.")
            else:
                try:
                    with st.spinner("AI is categorizing your transactions..."):
                        categorized = categorize_with_gemini(data, api_key, model_name)
                        data["category"] = [categorized.get(i, ("Other", ""))[0] for i in range(len(data))]
                        data["AI reason"] = [categorized.get(i, ("Other", "Not returned by AI"))[1] for i in range(len(data))]
                        st.session_state["categorized_data"] = data
                except Exception as e:
                    st.error(f"Could not categorize transactions: {e}")

    except Exception as e:
        st.error(f"Could not read the CSV: {e}")

if "categorized_data" in st.session_state:
    result = st.session_state["categorized_data"]
    st.subheader("2. Categorized transactions")
    st.dataframe(result, use_container_width=True)
    st.download_button("⬇️ Download categorized CSV", result.to_csv(index=False).encode("utf-8"), "categorized_expenses.csv", "text/csv")

    summary = result.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    total = result["amount"].sum()
    c1, c2 = st.columns(2)
    c1.metric("Total recorded spending", f"₹{total:,.2f}")
    c2.metric("Number of transactions", len(result))

    st.subheader("3. Spending summary")
    st.dataframe(summary.rename(columns={"category":"Category", "amount":"Total amount (₹)"}), use_container_width=True)
    fig, ax = plt.subplots()
    ax.bar(summary["category"], summary["amount"])
    ax.set_xlabel("Category")
    ax.set_ylabel("Amount (₹)")
    ax.set_title("Expenses by category")
    plt.xticks(rotation=35, ha="right")
    st.pyplot(fig)

    st.subheader("4. Monthly summary")
    monthly = result.assign(month=result["date"].dt.to_period("M").astype(str)).groupby("month", as_index=False)["amount"].sum()
    st.dataframe(monthly.rename(columns={"month":"Month", "amount":"Total amount (₹)"}), use_container_width=True)

    if not summary.empty:
        largest = summary.iloc[0]
        st.subheader("5. Simple spending insight")
        st.write(f"Your highest spending category is **{largest['category']}** (₹{largest['amount']:,.2f}). Review this category first when planning a budget.")
        st.caption("This is a basic educational insight, not professional financial advice.")
else:
    st.markdown("### Try the sample file")
    st.write("Download `sample_transactions.csv` from the project folder, then upload it above.")
