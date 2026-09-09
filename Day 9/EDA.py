import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

os.chdir(os.path.dirname(os.path.abspath(__file__)))
plt.rcParams["figure.dpi"] = 120

df = pd.read_csv("cleaned_employees.csv", parse_dates=["join_date"])
df["join_year"] = df["join_date"].dt.year

print("=" * 60)
print("DESCRIPTIVE STATISTICS - NUMERIC COLUMNS")
print("=" * 60)
print(df[["age", "salary_usd"]].describe().round(2))

print("\n" + "=" * 60)
print("HEADCOUNT BY DEPARTMENT")
print("=" * 60)
print(df["department"].value_counts())

print("\n" + "=" * 60)
print("SALARY STATS BY DEPARTMENT")
print("=" * 60)
salary_by_dept = df.groupby("department", observed=True)["salary_usd"].agg(
    ["mean", "median", "min", "max", "count"]
).round(0)
print(salary_by_dept)

print("\n" + "=" * 60)
print("HIRES BY YEAR")
print("=" * 60)
hires_by_year = df.dropna(subset=["join_year"]).groupby(
    df["join_year"].dropna().astype(int)
).size()
print(hires_by_year)

print("\n" + "=" * 60)
print("AGE-SALARY CORRELATION")
print("=" * 60)
corr = df["age"].corr(df["salary_usd"])
print(f"Pearson correlation (age vs salary): {corr:.3f}")

fig, ax = plt.subplots(figsize=(7, 5))
order = salary_by_dept["mean"].sort_values(ascending=False)
bars = ax.bar(order.index, order.values, color="#4C72B0")
ax.set_title("Average Salary by Department")
ax.set_ylabel("Average Salary (USD)")
ax.set_xlabel("Department")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, h + 500, f"${h:,.0f}",
            ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.savefig("1_avg_salary_by_department.png")
plt.close()

fig, ax = plt.subplots(figsize=(6, 6))
dept_counts = df["department"].value_counts()
ax.pie(dept_counts.values, labels=dept_counts.index, autopct="%1.0f%%",
       startangle=90, colors=plt.cm.Set2.colors)
ax.set_title("Headcount Distribution by Department")
plt.tight_layout()
plt.savefig("2_headcount_by_department.png")
plt.close()

fig, ax = plt.subplots(figsize=(7, 5))
ax.hist(df["age"], bins=6, color="#55A868", edgecolor="white")
ax.set_title("Employee Age Distribution")
ax.set_xlabel("Age")
ax.set_ylabel("Number of Employees")
plt.tight_layout()
plt.savefig("3_age_distribution.png")
plt.close()

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(hires_by_year.index, hires_by_year.values, marker="o",
        color="#C44E52", linewidth=2)
ax.set_title("Hiring Trend Over Time")
ax.set_xlabel("Join Year")
ax.set_ylabel("Number of Hires")
ax.set_xticks(hires_by_year.index)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("4_hiring_trend.png")
plt.close()

fig, ax = plt.subplots(figsize=(7, 5))
depts = df["department"].unique()
colors = plt.cm.Set2.colors
for i, dept in enumerate(depts):
    subset = df[df["department"] == dept]
    ax.scatter(subset["age"], subset["salary_usd"], label=dept,
               color=colors[i % len(colors)], s=80, edgecolor="black")
ax.set_title("Age vs Salary by Department")
ax.set_xlabel("Age")
ax.set_ylabel("Salary (USD)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend(title="Department")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("5_age_vs_salary.png")
plt.close()

print("\nAll 5 visualizations saved.")