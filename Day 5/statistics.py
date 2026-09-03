"""
Pandas Basics Walkthrough
-------------------------
Covers: loading a CSV, inspecting rows, checking shape, finding missing
values, filtering with conditions, and summary statistics.

To use with your own data, just change CSV_PATH below.
"""

import pandas as pd

# 1. Load a CSV dataset
CSV_PATH = "sample_data.csv"
df = pd.read_csv(CSV_PATH)

# 2. Display the first and last five rows
print("=== First 5 rows (df.head()) ===")
print(df.head())

print("\n=== Last 5 rows (df.tail()) ===")
print(df.tail())

# 3. Check the number of rows and columns
print("\n=== Shape (rows, columns) ===")
print(df.shape)
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

# 4. Find missing values
print("\n=== Missing values per column ===")
print(df.isnull().sum())

print("\n=== Total missing values in dataset ===")
print(df.isnull().sum().sum())

print("\n=== Rows containing at least one missing value ===")
print(df[df.isnull().any(axis=1)])

# 5. Filter data using different conditions
print("\n=== Filter: Engineering department only ===")
print(df[df["department"] == "Engineering"])

print("\n=== Filter: salary > 70000 ===")
print(df[df["salary"] > 70000])

print("\n=== Filter: multiple conditions (Engineering AND age < 35) ===")
print(df[(df["department"] == "Engineering") & (df["age"] < 35)])

print("\n=== Filter: department is Marketing OR Sales ===")
print(df[df["department"].isin(["Marketing", "Sales"])])

print("\n=== Filter: city contains 'York' (string match) ===")
print(df[df["city"].str.contains("York")])

# 6. Display summary statistics of the dataset
print("\n=== Summary statistics (numeric columns) ===")
print(df.describe())

print("\n=== Summary statistics (all columns, incl. object dtype) ===")
print(df.describe(include="all"))

print("\n=== Data types & non-null counts (df.info()) ===")
df.info()