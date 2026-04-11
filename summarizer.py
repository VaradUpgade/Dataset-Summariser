import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
 
# ── Model Loading ─────────────────────────────────────────────────────────────
MODEL_NAME = "google/flan-t5-base"
 
_model = None
_tokenizer = None
 
 
def _load_model():
    """Load model and tokenizer once, cache in memory for reuse."""
    global _model, _tokenizer
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        _model.eval()
    return _model, _tokenizer
 
 
def _build_prompt(analysis: dict) -> str:
    """Build a structured plain-text prompt from dataset analysis metadata."""
 
    numeric_info = "None"
    if analysis["numeric_summary"]:
        parts = []
        for col, stats in list(analysis["numeric_summary"].items())[:4]:
            parts.append(f"{col} (min={stats['min']}, max={stats['max']}, mean={stats['mean']})")
        numeric_info = "; ".join(parts)
 
    text_info = "None"
    if analysis["text_insights"]:
        parts = []
        for col, vals in list(analysis["text_insights"].items())[:3]:
            top = list(vals.keys())[:2]
            parts.append(f"{col}: top values are {', '.join(str(v) for v in top)}")
        text_info = "; ".join(parts)
 
    prompt = f"""Analyze this dataset and write a professional summary report.
 
Dataset facts:
- Rows: {analysis['rows']}, Columns: {analysis['columns']}
- Column names: {', '.join(analysis['column_names'])}
- Data types: {json.dumps(analysis['dtype_counts'])}
- Missing cells: {analysis['missing_cells']} ({analysis['missing_pct']}%)
- Duplicate rows: {analysis['duplicate_rows']}
- Numeric columns: {', '.join(analysis['numeric_cols']) if analysis['numeric_cols'] else 'None'}
- Text columns: {', '.join(analysis['text_cols'][:8]) if analysis['text_cols'] else 'None'}
- Columns with over 50% nulls: {', '.join(analysis['high_null_cols']) if analysis['high_null_cols'] else 'None'}
- Potential ID columns: {', '.join(analysis['potential_id_cols']) if analysis['potential_id_cols'] else 'None'}
- Numeric stats: {numeric_info}
- Text column top values: {text_info}
 
Write a clear summary covering: what the dataset is about, its size, data quality issues, types of data, notable patterns, and what it could be used for."""
 
    return prompt
 
 
def _post_process(raw_text: str, analysis: dict) -> str:
    """Combine structured stats block with the AI generated text."""
    dtype_lines = "\n".join([f"  • {k}: {v} column(s)" for k, v in analysis["dtype_counts"].items()])
 
    null_warning = ""
    if analysis["high_null_cols"]:
        null_warning = f"\n⚠️ **High Null Columns (>50%):** {', '.join(analysis['high_null_cols'])}"
 
    dup_warning = ""
    if analysis["duplicate_rows"] > 0:
        dup_warning = f"\n⚠️ **Duplicate Rows Detected:** {analysis['duplicate_rows']}"
 
    report = f"""**📋 Dataset Overview**
- **Shape:** {analysis['rows']:,} rows × {analysis['columns']} columns
- **Missing Data:** {analysis['missing_cells']:,} cells ({analysis['missing_pct']}%)
- **Duplicate Rows:** {analysis['duplicate_rows']}
 
**📊 Column Types**
{dtype_lines}{null_warning}{dup_warning}
 
**🤖 AI Analysis**
{raw_text.strip()}
"""
    return report
 
 
def generate_summary(analysis: dict) -> str:
    """
    Main function called by app.py.
    Loads flan-t5-base locally, runs inference, returns formatted report.
    """
    try:
        model, tokenizer = _load_model()
 
        prompt = _build_prompt(analysis)
 
        # Tokenize with truncation to fit flan-t5's 512 token limit
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=500,
            padding=False
        )
 
        # Generate with no_grad for efficiency
        with torch.no_grad():
            output_ids = model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=300,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3,
            )
 
        raw_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return _post_process(raw_text, analysis)
 
    except Exception as e:
        # Fallback: return structured stats without AI text
        dtype_lines = "\n".join([f"  • {k}: {v} column(s)" for k, v in analysis["dtype_counts"].items()])
        return f"""**📋 Dataset Overview**
- **Shape:** {analysis['rows']:,} rows × {analysis['columns']} columns
- **Missing Data:** {analysis['missing_cells']:,} cells ({analysis['missing_pct']}%)
- **Duplicate Rows:** {analysis['duplicate_rows']}
 
**📊 Column Types**
{dtype_lines}
 
**⚠️ AI Model Error**
Could not generate AI summary: {str(e)}
 
_You can still explore your dataset using the Column Analysis, Statistics, and Data Preview tabs._"""