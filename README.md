# 🔬 Dataset Summariser

An AI-powered web app that analyses any CSV/Excel/JSON dataset and generates a smart summary report using Claude AI.

## Features
- 📎 Load dataset via URL or file upload (CSV, Excel, JSON)
- 📊 Instant structural analysis — rows, columns, types, nulls, duplicates
- 🤖 AI-generated natural language summary report (Claude API)
- 📥 Downloadable report as `.txt`
- 🎨 Clean dark-themed Streamlit UI

---

## Setup Instructions

### 1. Clone / Download the project
```bash
cd dataset-summariser
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API key
```bash
cp .env.example .env
# Edit .env and paste your Anthropic API key
```

Get your key from: https://console.anthropic.com/

### 5. Run the app
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Project Structure

```
dataset-summariser/
├── app.py            # Streamlit UI & app logic
├── analyzer.py       # Dataset analysis (pandas-based)
├── summarizer.py     # Claude API integration
├── requirements.txt  # Python dependencies
├── .env.example      # API key template
└── README.md
```

---

## Sample Dataset URLs to Test

- Titanic: `https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv`
- Iris: `https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv`
- World Population: `https://raw.githubusercontent.com/datasets/population/master/data/population.csv`

---

## Tech Stack
- **Python** — core language
- **Streamlit** — web UI framework
- **Pandas / NumPy** — data analysis
- **Anthropic Claude API** — AI summary generation
