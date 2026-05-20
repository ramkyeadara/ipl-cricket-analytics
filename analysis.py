import pandas as pd
import os

# ---- Load all IPL data ----
ipl_path = r"C:\Projects\cricket\ipl"
all_deliveries = []
all_info = []

for filename in os.listdir(ipl_path):
    filepath = os.path.join(ipl_path, filename)
    if filename.endswith("_info.csv"):
        df = pd.read_csv(filepath, header=None, names=["type", "key", "value"], on_bad_lines='skip')
        df["match_id"] = filename.replace("_info.csv", "")
        all_info.append(df)
    elif filename.endswith(".csv") and "_info" not in filename:
        df = pd.read_csv(filepath)
        df["match_id"] = filename.replace(".csv", "")
        all_deliveries.append(df)

deliveries = pd.concat(all_deliveries, ignore_index=True)
info = pd.concat(all_info, ignore_index=True)

# ---- Get season for each match ----
seasons = info[info["key"] == "season"][["match_id", "value"]].rename(columns={"value": "season"})

# ---- Merge season into deliveries ----
deliveries = deliveries.merge(seasons, on="match_id", how="left")
deliveries = deliveries.merge(seasons, on="match_id", how="left")
print("Columns after merge:", list(deliveries.columns))
print("Season sample:", deliveries["season"].head(3).tolist())

# ---- Filter to 2021 onwards ----
deliveries = deliveries[deliveries["season"].isin(["2021","2022","2023","2024","2025","2026"])]

print(f"Loaded {len(deliveries):,} deliveries (2021 onwards)")
print(f"Seasons: {sorted(deliveries['season'].unique())}")

# ---- ANALYSIS 1: Batter Strike Rates ----
print()
print("=== TOP 10 BATTERS BY STRIKE RATE (min 200 balls) ===")
batter_stats = deliveries.groupby("striker").agg(
    runs=("runs_off_bat", "sum"),
    balls=("runs_off_bat", "count")
).reset_index()
batter_stats["strike_rate"] = (batter_stats["runs"] / batter_stats["balls"] * 100).round(2)
top_sr = batter_stats[batter_stats["balls"] >= 200].sort_values("strike_rate", ascending=False).head(10)
print(top_sr[["striker", "runs", "balls", "strike_rate"]].to_string(index=False))

# ---- ANALYSIS 2: Bowler Economy Rates ----
print()
print("=== TOP 10 BOWLERS BY ECONOMY (min 120 balls) ===")
bowler_stats = deliveries.groupby("bowler").agg(
    runs_conceded=("runs_off_bat", "sum"),
    balls=("runs_off_bat", "count")
).reset_index()
bowler_stats["economy"] = (bowler_stats["runs_conceded"] / bowler_stats["balls"] * 6).round(2)
top_economy = bowler_stats[bowler_stats["balls"] >= 120].sort_values("economy").head(10)
print(top_economy[["bowler", "runs_conceded", "balls", "economy"]].to_string(index=False))

# ---- ANALYSIS 3: Highest scoring venues ----
print()
print("=== TOP 10 HIGHEST SCORING VENUES (1st innings avg) ===")
first_innings = deliveries[deliveries["innings"] == 1]
venue_scores = first_innings.groupby(["match_id", "venue"])["runs_off_bat"].sum().reset_index()
venue_avg = venue_scores.groupby("venue")["runs_off_bat"].mean().sort_values(ascending=False).head(10)
print(venue_avg.round(1).to_string())

# ---- ANALYSIS 4: Toss impact ----
print()
print("=== TOSS IMPACT: BAT vs FIELD FIRST (2021 onwards) ===")
recent_match_ids = deliveries["match_id"].unique()
recent_info = info[info["match_id"].isin(recent_match_ids)]
toss = recent_info[recent_info["key"] == "toss_decision"]["value"].value_counts()
print(toss)