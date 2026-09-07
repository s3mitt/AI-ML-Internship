# Netflix Dataset Analysis

## Project Overview
Exploratory analysis of the Netflix Movies & TV Shows catalog (as of 2021),
covering data cleaning, basic statistical analysis, and visualizations.

**Dataset:** `netflix_titles.csv` — 7,787 titles, 12 columns
(show_id, type, title, director, cast, country, date_added, release_year,
rating, duration, listed_in, description).
Source: [TidyTuesday / Kaggle Netflix Movies and TV Shows dataset].

## Project Structure
```
netflix_dataset_analysis/
├── data/
│   └── netflix_titles.csv       # raw dataset
├── outputs/
│   ├── 1_bar_top_countries.png
│   ├── 2_line_titles_per_year.png
│   ├── 3_histogram_movie_duration.png
│   ├── 4_pie_movie_vs_tvshow.png
│   └── 5_bar_top_genres.png     # bonus chart
├── scripts/
│   └── analysis.py              # load, clean, analyze, visualize
└── README.md                    # this file
```

## How to Run
```bash
pip install pandas matplotlib seaborn
cd scripts
python analysis.py
```
Charts are written to `../outputs/`. All paths in the script are relative
to the script's own location, so it works regardless of your current
working directory.

## Data Cleaning Steps
- Missing `director`, `cast`, and `country` values filled with `"Unknown"`
  (too many gaps to drop — over 30% of rows were missing `director`).
- Rows missing `date_added` or `rating` dropped (fewer than 20 rows combined).
- Duplicate rows removed.
- `date_added` parsed into a proper datetime and a `year_added` column derived.
- Movie `duration` (e.g. `"90 min"`) parsed into a numeric `duration_min` column.

## Key Insights

1. **Movies dominate the catalog.** 5,372 titles (69%) are movies vs. 2,398
   (31%) TV shows — Netflix's library is still primarily film-first even
   though it's known for original series.

2. **The U.S. leads content production by a wide margin**, with 3,287
   titles — more than 3x India (990), the second-largest contributor,
   followed by the UK (721) and Canada (412).

3. **Content additions exploded between 2016 and 2019.** Titles added per
   year jumped from 440 (2016) to 2,153 (2019), a roughly 5x increase,
   reflecting Netflix's aggressive global content push during that period.

4. **2020 additions dipped slightly from 2019** (2,009 vs. 2,153) — likely
   tied to production slowdowns during the pandemic — and 2021 data is
   incomplete in this snapshot (only 117 titles), since the dataset was
   captured mid-year.

5. **The typical movie runs 86–114 minutes**, with a median of 98 minutes;
   the distribution is fairly tight around the 90–100 minute mark, which
   is standard feature-length runtime.

6. **TV-MA is the single most common rating** (2,861 titles, ~37%),
   followed by TV-14 (1,928) — together mature-audience ratings account
   for well over half the catalog, suggesting Netflix skews toward
   adult-oriented content rather than family programming.

7. **"International Movies" and "Dramas" are the two most common genre
   tags** (2,437 and 2,105 titles respectively), reinforcing that Netflix's
   catalog leans heavily on drama and non-domestic (to the US) content to
   fill out its library.

8. **Family-friendly ratings are a small minority.** TV-Y, TV-Y7, PG, and
   TV-G combined account for under 1,000 titles out of 7,770 — roughly
   13% of the catalog — versus the ~60%+ that carry mature ratings.
