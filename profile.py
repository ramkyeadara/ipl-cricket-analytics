import pandas as pd

# ---- Load clean data ----
deliveries = pd.read_parquet(r"C:\Projects\cricket\data\deliveries_clean.parquet")
info       = pd.read_parquet(r"C:\Projects\cricket\data\info_clean.parquet")

print("=" * 60)
print("DATA QUALITY PROFILE REPORT - IPL CRICKET")
print("=" * 60)

# ---- CHECK 1: Basic shape ----
print()
print("CHECK 1 - BASIC SHAPE")
print(f"  Deliveries rows    : {len(deliveries):,}")
print(f"  Deliveries columns : {len(deliveries.columns)}")
print(f"  Info rows          : {len(info):,}")
print(f"  Column names       : {list(deliveries.columns)}")

# ---- CHECK 2: Null values ----
print()
print("CHECK 2 - NULL VALUES (missing data)")
nulls     = deliveries.isnull().sum()
null_pct  = (deliveries.isnull().sum() / len(deliveries) * 100).round(2)
null_report = pd.DataFrame({"null_count": nulls, "null_pct": null_pct})
null_report = null_report[null_report["null_count"] > 0]
if len(null_report) == 0:
    print("  No null values found!")
else:
    print("  Columns with nulls:")
    print(null_report.to_string())

# ---- CHECK 3: Unique value counts ----
print()
print("CHECK 3 - UNIQUE VALUE COUNTS")
key_columns = ["venue", "batting_team", "bowling_team", "striker", "bowler", "season", "wicket_type"]
for col in key_columns:
    if col in deliveries.columns:
        print(f"  {col:20} : {deliveries[col].nunique():,} unique values")

# ---- CHECK 4: Venue names ----
print()
print("CHECK 4 - ALL VENUES (do names look consistent?)")
venue_counts = deliveries["venue"].value_counts()
for venue, count in venue_counts.items():
    print(f"  {count:6,} balls  ->  {venue}")

# ---- CHECK 5: Team names ----
print()
print("CHECK 5 - ALL TEAMS (any old names still there?)")
all_teams = pd.concat([
    deliveries["batting_team"],
    deliveries["bowling_team"]
]).value_counts()
for team, count in all_teams.items():
    print(f"  {count:6,}  ->  {team}")

# ---- CHECK 6: Numeric ranges ----
print()
print("CHECK 6 - NUMERIC RANGES (any impossible values?)")
numeric_cols = ["runs_off_bat", "extras", "wides", "noballs"]
for col in numeric_cols:
    if col in deliveries.columns:
        print(f"  {col:20} -> min: {deliveries[col].min()}, max: {deliveries[col].max()}, avg: {deliveries[col].mean().round(2)}")

# ---- CHECK 7: Season check ----
print()
print("CHECK 7 - ALL SEASONS (any weird formats?)")
seasons = info[info["key"] == "season"]["value"].value_counts().sort_index()
for season, count in seasons.items():
    flag = "WEIRD FORMAT -" if "/" in str(season) else "OK -"
    print(f"  {flag} {season} : {count} matches")

# ---- CHECK 8: Extras breakdown ----
print()
print("CHECK 8 - EXTRAS BREAKDOWN")
print(f"  Legal deliveries : {deliveries['is_legal'].sum():,}")
print(f"  Wides            : {deliveries['is_wide'].sum():,}")
print(f"  No balls         : {deliveries['is_noball'].sum():,}")
total = len(deliveries)
print(f"  Wide %           : {round(deliveries['is_wide'].sum()/total*100,2)}%")
print(f"  No ball %        : {round(deliveries['is_noball'].sum()/total*100,2)}%")

# ---- CHECK 9: Wicket types ----
print()
print("CHECK 9 - WICKET TYPES (do these make cricket sense?)")
wicket_types = deliveries["wicket_type"].value_counts()
for wtype, count in wicket_types.items():
    print(f"  {count:6,}  ->  {wtype}")

# ---- SUMMARY ----
print()
print("=" * 60)
print("PROFILE SUMMARY")
print(f"  Total deliveries : {len(deliveries):,}")
print(f"  Total matches    : {deliveries['match_id'].nunique():,}")
print(f"  Total batters    : {deliveries['striker'].nunique():,}")
print(f"  Total bowlers    : {deliveries['bowler'].nunique():,}")
print(f"  Total venues     : {deliveries['venue'].nunique():,}")
print("=" * 60)