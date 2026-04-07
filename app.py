import streamlit as st
import pandas as pd
from analyzer import analyze_dataset
from summarizer import generate_summary
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dataset Summariser",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
}

code, .mono {
    font-family: 'Space Mono', monospace !important;
}

.metric-card {
    background: linear-gradient(135deg, #13131e 0%, #1a1a2e 100%);
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}

.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #7c6fff;
    font-family: 'Space Mono', monospace;
}

.metric-label {
    font-size: 0.8rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 4px;
}

.summary-box {
    background: linear-gradient(135deg, #0f1a2e 0%, #0a0f1a 100%);
    border: 1px solid #1e3a5f;
    border-left: 4px solid #7c6fff;
    border-radius: 8px;
    padding: 24px;
    line-height: 1.8;
    font-size: 1rem;
}

.section-header {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: #7c6fff;
    margin-bottom: 12px;
}

.tag {
    display: inline-block;
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-family: 'Space Mono', monospace;
    color: #aaa;
    margin: 3px;
}

.stButton > button {
    background: linear-gradient(135deg, #7c6fff, #5a4fcf) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(124,111,255,0.4) !important;
}

.stTextInput > div > div > input {
    background: #13131e !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.9rem !important;
    padding: 12px 16px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #7c6fff !important;
    box-shadow: 0 0 0 2px rgba(124,111,255,0.2) !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #2a2a4a;
}

.stTabs [data-baseweb="tab-list"] {
    background: #13131e;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #888;
    border-radius: 6px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: #7c6fff !important;
    color: white !important;
}

.upload-zone {
    border: 2px dashed #2a2a4a;
    border-radius: 12px;
    padding: 30px;
    text-align: center;
    background: #0d0d18;
    transition: border-color 0.2s;
}

.upload-zone:hover {
    border-color: #7c6fff;
}

hr {
    border-color: #2a2a4a !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🔬 Dataset Summariser")
st.markdown("<p style='color:#888;margin-top:-10px;'>Drop a dataset URL or upload a file — get an AI-powered summary report instantly.</p>", unsafe_allow_html=True)
st.markdown("---")

# ── Input Section ─────────────────────────────────────────────────────────────
col_url, col_or, col_upload = st.columns([5, 1, 4])

with col_url:
    st.markdown("<div class='section-header'>Dataset URL</div>", unsafe_allow_html=True)
    dataset_url = st.text_input(
        label="url",
        placeholder="https://raw.githubusercontent.com/.../dataset.csv",
        label_visibility="collapsed"
    )
    st.markdown("<p style='color:#555;font-size:0.78rem;margin-top:4px;'>Supports: GitHub raw CSV, direct CSV links</p>", unsafe_allow_html=True)

with col_or:
    st.markdown("<div style='text-align:center;padding-top:40px;color:#555;font-weight:700'>OR</div>", unsafe_allow_html=True)

with col_upload:
    st.markdown("<div class='section-header'>Upload File</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "upload",
        type=["csv", "xlsx", "xls", "json"],
        label_visibility="collapsed"
    )

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([2, 3, 2])
with btn_col:
    run_btn = st.button("⚡  Analyse Dataset")

st.markdown("---")

# ── Main Logic ────────────────────────────────────────────────────────────────
if run_btn:
    df = None

    # Load dataset
    with st.spinner("Loading dataset..."):
        try:
            if uploaded_file:
                name = uploaded_file.name.lower()
                if name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                elif name.endswith((".xlsx", ".xls")):
                    df = pd.read_excel(uploaded_file)
                elif name.endswith(".json"):
                    df = pd.read_json(uploaded_file)
            elif dataset_url.strip():
                url = dataset_url.strip()
                # Handle GitHub blob → raw conversion
                if "github.com" in url and "/blob/" in url:
                    url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                # Fetch via requests (bypasses SSL cert issues on Mac/Windows)
                import requests, io
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                response = requests.get(url, verify=False, timeout=15)
                response.raise_for_status()
                content = io.BytesIO(response.content)
                if url.endswith(".csv"):
                    df = pd.read_csv(content)
                elif url.endswith((".xlsx", ".xls")):
                    df = pd.read_excel(content)
                elif url.endswith(".json"):
                    df = pd.read_json(content)
                else:
                    df = pd.read_csv(content)  # try CSV as default
            else:
                st.warning("⚠️ Please provide a URL or upload a file.")
        except Exception as e:
            st.error(f"❌ Failed to load dataset: {e}")

    if df is not None:
        # Analyse
        with st.spinner("Analysing dataset structure..."):
            analysis = analyze_dataset(df)

        # ── Top Metrics ───────────────────────────────────────────────────────
        m1, m2, m3, m4, m5 = st.columns(5)
        metrics = [
            (m1, analysis["rows"], "Rows"),
            (m2, analysis["columns"], "Columns"),
            (m3, analysis["missing_cells"], "Missing Cells"),
            (m4, f"{analysis['missing_pct']}%", "Missing %"),
            (m5, analysis["duplicate_rows"], "Duplicate Rows"),
        ]
        for col, val, label in metrics:
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{val}</div>
                    <div class='metric-label'>{label}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Tabs ──────────────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI Summary", "📊 Column Analysis", "🔢 Statistics", "👁 Data Preview"])

        with tab1:
            with st.spinner("Generating AI summary..."):
                summary = generate_summary(analysis)
            st.markdown("<div class='section-header'>AI-Generated Report</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)

            # Download report
            st.markdown("<br>", unsafe_allow_html=True)
            report_text = f"""DATASET SUMMARY REPORT
{'='*50}

BASIC STATISTICS
----------------
Rows         : {analysis['rows']}
Columns      : {analysis['columns']}
Missing Cells: {analysis['missing_cells']} ({analysis['missing_pct']}%)
Duplicates   : {analysis['duplicate_rows']}

COLUMN TYPES
------------
{chr(10).join([f"  {k}: {v}" for k, v in analysis['dtype_counts'].items()])}

AI SUMMARY
----------
{summary}
"""
            st.download_button(
                "📥 Download Report (.txt)",
                data=report_text,
                file_name="dataset_summary_report.txt",
                mime="text/plain"
            )

        with tab2:
            st.markdown("<div class='section-header'>Column Details</div>", unsafe_allow_html=True)
            col_df = pd.DataFrame(analysis["column_details"])
            st.dataframe(col_df, use_container_width=True, hide_index=True)

            st.markdown("<br><div class='section-header'>Data Types Distribution</div>", unsafe_allow_html=True)
            dtype_data = pd.DataFrame(
                list(analysis["dtype_counts"].items()),
                columns=["Type", "Count"]
            )
            st.bar_chart(dtype_data.set_index("Type"))

        with tab3:
            st.markdown("<div class='section-header'>Numeric Statistics</div>", unsafe_allow_html=True)
            numeric_df = df.select_dtypes(include="number")
            if not numeric_df.empty:
                st.dataframe(numeric_df.describe().round(3), use_container_width=True)
            else:
                st.info("No numeric columns found.")

        with tab4:
            st.markdown("<div class='section-header'>First 100 Rows</div>", unsafe_allow_html=True)
            st.dataframe(df.head(100), use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>")
st.markdown("<p style='text-align:center;color:#333;font-size:0.78rem;'>Dataset Summariser · Built with Streamlit + Claude AI</p>", unsafe_allow_html=True)
