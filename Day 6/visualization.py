import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset (path relative to this script's own folder)
script_dir = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(script_dir, "sample_data.csv")
df = pd.read_csv(CSV_PATH)

sns.set_style("whitegrid")
OUT_DIR = script_dir

# ---------------------------------------------------------
# 1. BAR CHART — Average salary by department
# ---------------------------------------------------------
avg_salary = df.groupby("department")["salary"].mean().sort_values(ascending=False)

plt.figure(figsize=(7, 5))
sns.barplot(x=avg_salary.index, y=avg_salary.values, hue=avg_salary.index,
            palette="viridis", legend=False)
plt.title("Average Salary by Department")
plt.xlabel("Department")
plt.ylabel("Average Salary ($)")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "1_bar_chart_avg_salary.png"), dpi=150)
plt.close()

# ---------------------------------------------------------
# 2. LINE CHART — Salary trend by years of experience
# ---------------------------------------------------------
line_data = df.dropna(subset=["salary", "years_experience"]).sort_values("years_experience")

plt.figure(figsize=(7, 5))
plt.plot(line_data["years_experience"], line_data["salary"],
         marker="o", color="darkorange", linewidth=2)
plt.title("Salary vs. Years of Experience")
plt.xlabel("Years of Experience")
plt.ylabel("Salary ($)")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "2_line_chart_salary_experience.png"), dpi=150)
plt.close()

# ---------------------------------------------------------
# 3. HISTOGRAM — Age distribution
# ---------------------------------------------------------
plt.figure(figsize=(7, 5))
sns.histplot(df["age"], bins=6, kde=True, color="steelblue")
plt.title("Age Distribution")
plt.xlabel("Age")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "3_histogram_age.png"), dpi=150)
plt.close()

# ---------------------------------------------------------
# 4. PIE CHART — Employee count by department
# ---------------------------------------------------------
dept_counts = df["department"].value_counts()

plt.figure(figsize=(6, 6))
plt.pie(dept_counts.values, labels=dept_counts.index, autopct="%1.1f%%",
        startangle=90, colors=sns.color_palette("pastel"))
plt.title("Employee Share by Department")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "4_pie_chart_department.png"), dpi=150)
plt.close()

# ---------------------------------------------------------
# Print underlying numbers used to write observations
# ---------------------------------------------------------
print("Average salary by department:\n", avg_salary, "\n")
print("Age stats:\n", df["age"].describe(), "\n")
print("Department counts:\n", dept_counts, "\n")
print("Salary/experience correlation:", df["salary"].corr(df["years_experience"]))

print("\nAll charts saved successfully.")