import pandas as pd
import os

# ---- Load Silver data ----
deliveries = pd.read_parquet(r"C:\Projects\cricket\data\deliveries_clean.parquet")
info       = pd.read_parquet(r"C:\Projects\cricket\data\info_clean.parquet")

print(f"Deliveries loaded: {len(deliveries):,}")
print(f"Info loaded: {len(info):,}")

# ---- STEP 1: Calculate innings scores ----
innings_scores = deliveries.groupby(["match_id", "innings"]).agg(
    runs        = ("runs_off_bat", "sum"),
    extras      = ("extras", "sum"),
    wickets     = ("wicket_type", lambda x: (x != "not_out").sum()),
    legal_balls = ("is_legal", "sum")
).reset_index()

innings_scores["total_runs"] = innings_scores["runs"] + innings_scores["extras"]
innings_scores["overs"]      = (innings_scores["legal_balls"] / 6).round(1)

print(f"Innings scores calculated: {len(innings_scores):,} innings")

# ---- STEP 2: Split into first and second innings ----
innings1 = innings_scores[innings_scores["innings"] == 1][
    ["match_id", "total_runs", "wickets", "overs"]
].rename(columns={
    "total_runs" : "innings1_score",
    "wickets"    : "innings1_wickets",
    "overs"      : "innings1_overs"
})

innings2 = innings_scores[innings_scores["innings"] == 2][
    ["match_id", "total_runs", "wickets", "overs"]
].rename(columns={
    "total_runs" : "innings2_score",
    "wickets"    : "innings2_wickets",
    "overs"      : "innings2_overs"
})

# ---- STEP 3: Extract match info ----
def get_value(info_df, key):
    return info_df[info_df["key"] == key][["match_id", "value"]].rename(columns={"value": key})

season       = get_value(info, "season")
venue        = get_value(info, "venue")
toss_winner  = get_value(info, "toss_winner")
toss_dec     = get_value(info, "toss_decision")
winner       = get_value(info, "winner")
date         = get_value(info, "date")

# Get team1 and team2
teams = info[info["key"] == "team"][["match_id", "value"]]
team1 = teams.groupby("match_id")["value"].first().reset_index().rename(columns={"value": "team1"})
team2 = teams.groupby("match_id")["value"].last().reset_index().rename(columns={"value": "team2"})

# ---- STEP 4: Build match summary ----
match_summary = season.copy()
for df in [venue, toss_winner, toss_dec, winner, date, team1, team2]:
    match_summary = match_summary.merge(df, on="match_id", how="left")

match_summary = match_summary.merge(innings1, on="match_id", how="left")
match_summary = match_summary.merge(innings2, on="match_id", how="left")

# ---- STEP 5: Add result columns ----
match_summary["batting_first"] = match_summary.apply(
    lambda row: row["toss_winner"] if row["toss_decision"] == "bat"
    else (row["team2"] if row["toss_winner"] == row["team1"] else row["team1"]), axis=1
)

match_summary["chasing_team"] = match_summary.apply(
    lambda row: row["team2"] if row["batting_first"] == row["team1"] else row["team1"], axis=1
)

match_summary["result"] = match_summary.apply(
    lambda row: "Batting first won" if row["winner"] == row["batting_first"]
    else "Chasing won" if pd.notna(row["winner"]) else "No result", axis=1
)

match_summary["margin_runs"] = match_summary.apply(
    lambda row: row["innings1_score"] - row["innings2_score"]
    if row["result"] == "Batting first won" else None, axis=1
)

# ---- STEP 6: Clean up and save ----
match_summary = match_summary.rename(columns={
    "season"        : "season",
    "venue"         : "venue",
    "toss_winner"   : "toss_winner",
    "toss_decision" : "toss_decision",
    "winner"        : "winner",
    "date"          : "match_date",
})

# Sort by match date — latest matches last
match_summary["match_date"] = pd.to_datetime(match_summary["match_date"], errors="coerce")
match_summary = match_summary.sort_values("match_date").reset_index(drop=True)

# Fix season formats
season_map = {"2007/08": "2008", "2009/10": "2010", "2020/21": "2020"}
match_summary["season"] = match_summary["season"].replace(season_map)

print(f"Match summary rows: {len(match_summary):,}")
print(f"Columns: {list(match_summary.columns)}")
print()
print("=== SAMPLE (last 5 matches) ===")
print(match_summary.tail(5)[["season", "venue", "team1", "team2", "innings1_score", "innings2_score", "winner", "result"]].to_string())

# ---- Save Gold layer ----
output_path = r"C:\Projects\cricket\data"
match_summary.to_parquet(f"{output_path}\\match_summary.parquet", index=False)

print()
print("=== SAVED SUCCESSFULLY ===")
print(f"match_summary.parquet — {len(match_summary):,} rows")
print(f"Location: {output_path}")