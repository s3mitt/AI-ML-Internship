"""Data Analyzer Tool: Statistical and structural profiling for tabular datasets (CSV/JSON)."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from core.errors import ResourceNotFoundError, SecurityError, ValidationError
from tools.base import BaseTool

DEFAULT_BASE_DIR = Path(__file__).resolve().parent.parent


class DataAnalyzerTool(BaseTool):
    """Analyzes tabular datasets from file paths or chained tool outputs."""

    name = "data_analyzer"
    description = (
        "Analyze CSV/JSON datasets or tabular records. Computes row/column counts, "
        "missing value tallies, descriptive metrics (mean, median, min, max), group aggregations, and correlations."
    )
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to CSV or JSON file to analyze.",
            },
            "data": {
                "type": "array",
                "description": "Direct list of dictionary records to analyze (e.g. from Database or File Reader).",
            },
            "target_column": {
                "type": "string",
                "description": "Specific column to inspect or summarize.",
            },
            "group_by": {
                "type": "string",
                "description": "Column name to group by for aggregations.",
            },
        },
        "required": [],
    }
    examples = [
        {"file_path": "data/employees.csv"},
        {"file_path": "data/employees.csv", "group_by": "department"},
    ]

    def _load_dataframe(
        self,
        file_path: Optional[str] = None,
        data: Optional[List[Dict[str, Any]]] = None,
    ) -> pd.DataFrame:
        """Load DataFrame from file or in-memory list with validation."""
        if data is not None:
            if not isinstance(data, list) or len(data) == 0:
                raise ValidationError("Provided 'data' is empty or invalid format.", tool_name=self.name)
            try:
                df = pd.DataFrame(data)
                return df
            except Exception as e:
                raise ValidationError(f"Failed to parse in-memory records into table: {e}", tool_name=self.name)

        if not file_path or not str(file_path).strip():
            raise ValidationError("Either 'file_path' or 'data' must be supplied for analysis.", tool_name=self.name)

        p = (DEFAULT_BASE_DIR / file_path).resolve() if not Path(file_path).is_absolute() else Path(file_path).resolve()

        # Path traversal guard
        try:
            p.relative_to(DEFAULT_BASE_DIR)
        except ValueError:
            raise SecurityError(f"Access denied: '{file_path}' is outside project directory.", tool_name=self.name)

        if not p.exists() and (DEFAULT_BASE_DIR / "data" / file_path).exists():
            p = (DEFAULT_BASE_DIR / "data" / file_path).resolve()

        if not p.exists():
            raise ResourceNotFoundError(f"File not found: '{file_path}'", tool_name=self.name)

        ext = p.suffix.lower()
        try:
            if ext == ".csv":
                df = pd.read_csv(p)
            elif ext == ".json":
                with open(p, "r", encoding="utf-8") as f:
                    raw_json = json.load(f)
                if isinstance(raw_json, list):
                    df = pd.DataFrame(raw_json)
                elif isinstance(raw_json, dict):
                    # Flatten or extract tabular sub-array
                    candidates = [v for v in raw_json.values() if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict)]
                    if candidates:
                        df = pd.DataFrame(candidates[0])
                    else:
                        df = pd.json_normalize(raw_json)
                else:
                    raise ValidationError("JSON content is not a list or dictionary.", tool_name=self.name)
            else:
                raise ValidationError(f"Unsupported file format '{ext}' for data analysis. Use .csv or .json.", tool_name=self.name)
        except pd.errors.EmptyDataError:
            raise ValidationError(f"File '{p.name}' is completely empty.", tool_name=self.name)
        except Exception as e:
            if isinstance(e, (ValidationError, SecurityError, ResourceNotFoundError)):
                raise e
            raise ValidationError(f"Failed to parse file for data analysis: {str(e)}", tool_name=self.name)

        if df.empty:
            raise ValidationError(f"Dataset in '{p.name}' has 0 rows.", tool_name=self.name)

        return df

    def run(
        self,
        file_path: Optional[str] = None,
        data: Optional[List[Dict[str, Any]]] = None,
        target_column: Optional[str] = None,
        group_by: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Run statistical profiling on the dataset."""
        df = self._load_dataframe(file_path=file_path, data=data)

        total_rows = int(len(df))
        columns = list(df.columns)
        missing_counts = {col: int(df[col].isna().sum()) for col in columns}

        # Check numeric stats
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        statistics: Dict[str, Any] = {}

        for col in numeric_cols:
            series = df[col].dropna()
            if not series.empty:
                statistics[col] = {
                    "mean": round(float(series.mean()), 2),
                    "median": round(float(series.median()), 2),
                    "min": round(float(series.min()), 2),
                    "max": round(float(series.max()), 2),
                    "count": int(series.count()),
                }

        # Validate target column if provided
        target_summary = None
        if target_column:
            if target_column not in columns:
                raise ValidationError(
                    f"Target column '{target_column}' not found. Available columns: {columns}",
                    tool_name=self.name,
                )
            if target_column in statistics:
                target_summary = statistics[target_column]
            else:
                # Categorical summary
                val_counts = df[target_column].value_counts().head(5).to_dict()
                target_summary = {"unique_values": int(df[target_column].nunique()), "top_values": val_counts}

        # Group-by analysis
        group_summary = None
        if group_by:
            if group_by not in columns:
                raise ValidationError(
                    f"Grouping column '{group_by}' not found. Available columns: {columns}",
                    tool_name=self.name,
                )
            grouped = df.groupby(group_by)
            group_res = {}
            for name, group in grouped:
                entry = {"row_count": int(len(group))}
                for num_col in numeric_cols:
                    if num_col != group_by:
                        entry[f"avg_{num_col}"] = round(float(group[num_col].mean()), 2)
                group_res[str(name)] = entry
            group_summary = group_res

        # Pairwise correlations if multiple numeric columns
        correlations = None
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr().round(3).to_dict()
            correlations = corr_matrix

        output: Dict[str, Any] = {
            "rows": total_rows,
            "columns": columns,
            "column_count": len(columns),
            "missing_values": missing_counts,
            "statistics": statistics,
        }

        if target_summary:
            output["target_summary"] = target_summary
        if group_summary:
            output["group_by"] = {"column": group_by, "groups": group_summary}
        if correlations:
            output["correlations"] = correlations

        return output
