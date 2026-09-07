import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "netflix_titles.csv")
OUT_DIR = SCRIPT_DIR

sns.set_style("whitegrid")

df = pd.read_csv(DATA_PATH)
print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns\n")

print("=== Missing values before cleaning ===")
print(df.isnull().sum(), "\n")

# director/cast/country: replace missing with "Unknown" (categorical text field)
for col in ["director", "cast", "country"]:
    df[col] = df[col].fillna("Unknown")

# date_added/rating/duration: drop the handful of rows missing these,
# since they're needed for time-trend and duration analysis
df = df.dropna(subset=["date_added", "rating", "duration"])

# Remove exact duplicate rows, if any
df = df.drop_duplicates()

# Parse date_added into a real datetime and extract year
df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
df = df.dropna(subset=["date_added"])
df["year_added"] = df["date_added"].dt.year

print("=== Missing values after cleaning ===")
print(df.isnull().sum(), "\n")
print(f"Rows after cleaning: {df.shape[0]}\n")

type_counts = df["type"].value_counts()
print("=== Content type breakdown ===")
print(type_counts, "\n")

top_countries = df["country"][df["country"] != "Unknown"].str.split(", ").explode().value_counts().head(10)
print("=== Top 10 countries by title count ===")
print(top_countries, "\n")

titles_per_year = df["year_added"].value_counts().sort_index()
print("=== Titles added per year ===")
print(titles_per_year, "\n")

rating_counts = df["rating"].value_counts().head(10)
print("=== Top content ratings ===")
print(rating_counts, "\n")

# Movie duration in minutes (only rows where duration is "X min")
movie_durations = df[df["type"] == "Movie"].copy()
movie_durations["duration_min"] = (
    movie_durations["duration"].str.extract(r"(\d+)").astype(float)
)
print("=== Movie duration stats (minutes) ===")
print(movie_durations["duration_min"].describe(), "\n")

top_genres = df["listed_in"].str.split(", ").explode().value_counts().head(10)
print("=== Top 10 genres ===")
print(top_genres, "\n")

# --- Chart 1: Bar chart — Top 10 countries by title count
plt.figure(figsize=(9, 5))
sns.barplot(x=top_countries.index, y=top_countries.values, legend=False)
plt.title("Top 10 Countries by Number of Netflix Titles")
plt.xlabel("Country")
plt.ylabel("CountryNumber of Titles")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "1_bar_top_countries.png"), dpi=150)
plt.close()

# --- Chart 2: Line chart — Titles added to Netflix per year
plt.figure(figsize=(9, 5))
plt.plot(titles_per_year.index, titles_per_year.values, marker="s")
plt.title("Netflix Titles Added per Year")
plt.xlabel("Year Added")
plt.ylabel("Number of Titles")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "2_line_titles_per_year.png"), dpi=150)
plt.close()

# --- Chart 3: Histogram — Movie duration distribution
plt.figure(figsize=(9, 5))
sns.histplot(movie_durations["duration_min"].dropna(), bins=40)
plt.title("Distribution of Movie Durations")
plt.xlabel("Duration (minutes)")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "3_histogram_movie_duration.png"), dpi=150)
plt.close()

# --- Chart 4: Pie chart — Movie vs TV Show split
plt.figure(figsize=(6, 6))
plt.pie(type_counts.values, labels=type_counts.index, autopct="%1.1f%%",
        startangle=90, colors=sns.color_palette("pastel"))
plt.title("Movies vs. TV Shows on Netflix")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "4_pie_movie_vs_tvshow.png"), dpi=150)
plt.close()

# --- Chart 5 (bonus): Bar chart — Top 10 genres
plt.figure(figsize=(9, 5))
sns.barplot(x=top_genres.index, y=top_genres.values, legend=False)
plt.title("Top 10 Genres on Netflix")
plt.xlabel("Genre")
plt.ylabel("Number of Titles")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "5_bar_top_genres.png"), dpi=150)
plt.close()

print("All charts saved to the outputs/ folder.")