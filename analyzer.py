import pandas as pd
import numpy as np


def analyze_dataset(df: pd.DataFrame) -> dict:
    """
    Run a full structural analysis on a DataFrame and return a dict
    that can be fed into the AI summarizer or displayed directly.
    """
    rows, columns = df.shape
    missing_cells = int(df.isnull().sum().sum())
    missing_pct = round((missing_cells / (rows * columns)) * 100, 2) if rows * columns > 0 else 0
    duplicate_rows = int(df.duplicated().sum())

    # Column-level details
    column_details = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = int(df[col].isnull().sum())
        null_pct = round((null_count / rows) * 100, 1)
        unique_count = int(df[col].nunique())

        detail = {
            "Column": col,
            "Data Type": dtype,
            "Nulls": null_count,
            "Null %": f"{null_pct}%",
            "Unique Values": unique_count,
        }

        # Sample values (non-null)
        sample_vals = df[col].dropna().head(3).tolist()
        detail["Sample Values"] = ", ".join([str(v) for v in sample_vals])

        column_details.append(detail)

    # Data type breakdown
    dtype_map = {}
    for col in df.columns:
        kind = str(df[col].dtype)
        if "int" in kind or "float" in kind:
            category = "Numeric"
        elif "datetime" in kind:
            category = "Datetime"
        elif "bool" in kind:
            category = "Boolean"
        elif "object" in kind or "string" in kind or "category" in kind:
            category = "Text / Categorical"
        else:
            category = "Other"
        dtype_map[category] = dtype_map.get(category, 0) + 1

    # Numeric summary stats
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    numeric_summary = {}
    for col in numeric_cols:
        numeric_summary[col] = {
            "mean": round(float(df[col].mean()), 4) if not df[col].isnull().all() else None,
            "std": round(float(df[col].std()), 4) if not df[col].isnull().all() else None,
            "min": round(float(df[col].min()), 4) if not df[col].isnull().all() else None,
            "max": round(float(df[col].max()), 4) if not df[col].isnull().all() else None,
        }

    # Text column insights
    text_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    text_insights = {}
    for col in text_cols[:5]:  # Limit to first 5 text cols
        top_vals = df[col].value_counts().head(3)
        text_insights[col] = {k: int(v) for k, v in top_vals.items()}

    # Potential ID columns (high uniqueness)
    potential_id_cols = [
        col for col in df.columns
        if df[col].nunique() == rows and rows > 10
    ]

    # Columns with high nulls
    high_null_cols = [
        col for col in df.columns
        if (df[col].isnull().sum() / rows) > 0.5
    ]

    return {
        "rows": rows,
        "columns": columns,
        "missing_cells": missing_cells,
        "missing_pct": missing_pct,
        "duplicate_rows": duplicate_rows,
        "column_names": df.columns.tolist(),
        "column_details": column_details,
        "dtype_counts": dtype_map,
        "numeric_summary": numeric_summary,
        "numeric_cols": numeric_cols,
        "text_cols": text_cols,
        "text_insights": text_insights,
        "potential_id_cols": potential_id_cols,
        "high_null_cols": high_null_cols,
    }
