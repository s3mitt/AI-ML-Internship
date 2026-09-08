"""
Cleans a messy employee records CSV file:
  1. Loads the dataset
  2. Identifies missing values (including disguised ones like "N/A", "unknown")
  3. Renames columns to clean, consistent snake_case names
  4. Converts columns to correct data types
  5. Handles missing values using column-appropriate techniques
  6. Removes duplicate records
  7. Saves the cleaned dataset to a new CSV file
  
"""

import os
import sys
import pandas as pd
import numpy as np

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def load_data(input_path: str) -> pd.DataFrame:
    """Step 1: Load dataset from CSV."""
    df = pd.read_csv("raw_employees.csv")
    print(f"Loaded '{"raw_employees.csv"}' -> shape: {df.shape}")
    return df


def flag_disguised_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Step 2: Identify missing values, including disguised placeholders."""
    df = df.replace({"N/A": np.nan, "n/a": np.nan, "unknown": np.nan, "": np.nan})
    print("\nMissing values per column (before handling):")
    print(df.isna().sum())
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Step 3: Rename columns to clean, consistent snake_case names."""
    df = df.rename(columns=lambda c: (
        c.strip()
         .lower()
         .replace(" ", "_")
         .replace("($)", "_usd")
         .replace("(", "")
         .replace(")", "")
    ))
    df = df.rename(columns={"emp_id": "employee_id", "dept": "department"})
    print("\nColumns renamed to:", list(df.columns))
    return df


def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Step 4: Convert columns to their correct data types."""
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["salary_usd"] = pd.to_numeric(df["salary_usd"], errors="coerce")
    df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce", format="mixed")
    df["department"] = df["department"].astype("category")
    df["full_name"] = df["full_name"].str.strip()

    print("\nData types after conversion:")
    print(df.dtypes)
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Step 5: Handle missing values with a technique suited to each column."""
    # Numeric: impute with median (robust to outliers)
    df["age"] = df["age"].fillna(df["age"].median()).astype(int)

    # Salary: impute using the median within the same department, then a global fallback
    df["salary_usd"] = df.groupby("department", observed=False)["salary_usd"].transform(
        lambda s: s.fillna(s.median())
    )
    df["salary_usd"] = df["salary_usd"].fillna(df["salary_usd"].median())

    # Categorical: explicit "Unknown" category instead of dropping rows
    df["department"] = df["department"].cat.add_categories(["Unknown"]).fillna("Unknown")

    # Text fields that can't be inferred: mark explicitly rather than guess
    df["full_name"] = df["full_name"].fillna("Unknown")
    df["email"] = df["email"].fillna("not_provided@unknown.com")

    # Dates: leave as NaT (a fabricated date could mislead), but flag it
    df["join_date_missing"] = df["join_date"].isna()

    print("\nMissing values after handling:")
    print(df.isna().sum())
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Step 6: Remove duplicate records."""
    before = len(df)
    df = df.drop_duplicates(subset=["employee_id"], keep="first")
    df = df.drop_duplicates()
    after = len(df)
    print(f"\nRemoved {before - after} duplicate row(s): {before} -> {after}")
    return df.reset_index(drop=True)


def save_data(df: pd.DataFrame, output_path: str) -> None:
    """Step 7: Save the cleaned dataset."""
    df.to_csv(output_path, index=False)
    print(f"\nCleaned dataset saved to '{output_path}'")
    print("\nFinal preview:")
    print(df.head())
    print("\nFinal shape:", df.shape)


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "raw_employees.csv"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "cleaned_employees.csv"

    df = load_data(input_path)
    df = flag_disguised_missing_values(df)
    df = rename_columns(df)
    df = convert_data_types(df)
    df = handle_missing_values(df)
    df = remove_duplicates(df)
    save_data(df, output_path)


if __name__ == "__main__":
    main()