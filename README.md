# Expense Categorizer (LLM Mini Project 62)

A Streamlit application that uses Google's Gemini API to categorize bank transaction descriptions and summarize spending.

## Features
- Upload a CSV with `date`, `description`, and `amount`
- Categorize transactions using GenAI
- View category totals and monthly totals
- View a bar chart and a short spending insight
- Download the categorized CSV

## Setup
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment:
   - Windows: `py -m venv venv` then `venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv venv` then `source venv/bin/activate`
4. Install packages: `pip install -r requirements.txt`
5. Run: `streamlit run app.py`
6. Paste your Gemini API key into the sidebar and upload `sample_transactions.csv`.

Get an API key from Google AI Studio: https://aistudio.google.com/

## CSV format
The file must have columns named `date`, `description`, and `amount`.

## Safety
Use sample or anonymized data. Do not upload account numbers, card numbers, passwords, or other sensitive banking information. Never commit your API key or `.env` file to GitHub.

## Project details
- Roll number: 62
- Project title: Expense Categorizer
- Stack: Python, Streamlit, Gemini API, Pandas, Matplotlib
