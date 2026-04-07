import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def generate_summary(analysis: dict) -> str:
    """
    Send dataset analysis to Google Gemini API and get back a human-readable summary report.
    """
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return "❌ **API Key Missing**: Please set your GEMINI_API_KEY in the `.env` file."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Build a structured prompt from analysis
    prompt = f"""
You are a data analyst assistant. I have analysed a dataset and will provide you its structural metadata.
Please generate a clear, insightful, and concise summary report of this dataset in plain English.

Your summary should cover:
1. A brief overall description of what this dataset likely contains (inferred from column names and types)
2. Size and shape (rows, columns)
3. Data quality observations (missing data, duplicates)
4. Types of data present (numeric, text, datetime, etc.)
5. Notable columns or patterns (potential ID columns, high-null columns, key numeric ranges)
6. A short recommendation on what this dataset could be used for

Keep it professional but readable. Use bullet points where helpful. Write 150-250 words.

--- DATASET METADATA ---
Rows: {analysis['rows']}
Columns: {analysis['columns']}
Column Names: {', '.join(analysis['column_names'])}
Data Types Breakdown: {json.dumps(analysis['dtype_counts'])}
Missing Cells: {analysis['missing_cells']} ({analysis['missing_pct']}%)
Duplicate Rows: {analysis['duplicate_rows']}
Numeric Columns: {', '.join(analysis['numeric_cols']) if analysis['numeric_cols'] else 'None'}
Text/Categorical Columns: {', '.join(analysis['text_cols'][:10]) if analysis['text_cols'] else 'None'}
Potential ID Columns: {', '.join(analysis['potential_id_cols']) if analysis['potential_id_cols'] else 'None'}
High-Null Columns (>50%): {', '.join(analysis['high_null_cols']) if analysis['high_null_cols'] else 'None'}
Numeric Stats (sample): {json.dumps(dict(list(analysis['numeric_summary'].items())[:5]), indent=2) if analysis['numeric_summary'] else 'N/A'}
Top Values in Text Columns (sample): {json.dumps(dict(list(analysis['text_insights'].items())[:3]), indent=2) if analysis['text_insights'] else 'N/A'}
--- END METADATA ---

Now write the summary report:
"""

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
            return "❌ **Invalid API Key**: Your Gemini API key is incorrect. Please check your `.env` file."
        elif "quota" in error_msg.lower():
            return "❌ **Quota Exceeded**: Free tier limit reached. Try again after some time."
        else:
            return f"❌ **AI Summary Error**: {error_msg}\n\nYou can still view the dataset statistics in the other tabs."
