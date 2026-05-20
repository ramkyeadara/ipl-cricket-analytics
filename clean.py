import pandas as pd
import os

# ---- Load all raw data ----
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

print(f"Raw deliveries loaded: {len(deliveries):,}")

# ---- Add season ----
seasons = info[info["key"] == "season"][["match_id", "value"]].rename(columns={"value": "season"})
deliveries = deliveries.merge(seasons, on="match_id", how="left")

# Drop duplicate season columns if they exist
if "season_x" in deliveries.columns:
    deliveries = deliveries.drop(columns=["season_x"])
if "season_y" in deliveries.columns:
    deliveries = deliveries.rename(columns={"season_y": "season"})

# ---- STEP 1: Fix venue names ----
venue_map = {
    "M Chinnaswamy Stadium, Bengaluru"                                     : "M Chinnaswamy Stadium",
    "M.Chinnaswamy Stadium"                                                : "M Chinnaswamy Stadium",
    "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh"    : "PCA Stadium Mohali",
    "Punjab Cricket Association Stadium, Mohali"                           : "PCA Stadium Mohali",
    "Rajiv Gandhi International Stadium, Uppal, Hyderabad"                 : "Rajiv Gandhi Stadium Hyderabad",
    "Rajiv Gandhi International Stadium, Uppal"                            : "Rajiv Gandhi Stadium Hyderabad",
    "Wankhede Stadium, Mumbai"                                             : "Wankhede Stadium",
    "Dr DY Patil Sports Academy, Mumbai"                                   : "Dr DY Patil Sports Academy",
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam"  : "ACA-VDCA Stadium Visakhapatnam",
    "Narendra Modi Stadium, Ahmedabad"                                     : "Narendra Modi Stadium",
    "Arun Jaitley Stadium, Delhi"                                          : "Arun Jaitley Stadium",
    "Eden Gardens, Kolkata"                                                : "Eden Gardens",
    "MA Chidambaram Stadium, Chepauk, Chennai"                             : "MA Chidambaram Stadium",
    "MA Chidambaram Stadium, Chepauk"                                      : "MA Chidambaram Stadium",
    "Sawai Mansingh Stadium, Jaipur"                                       : "Sawai Mansingh Stadium",
    "Himachal Pradesh Cricket Association Stadium, Dharamsala"             : "HPCA Stadium Dharamsala",
    "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh" : "MYSI Stadium Chandigarh",
}
deliveries["venue"] = deliveries["venue"].replace(venue_map)
print(f"Venues cleaned: {deliveries['venue'].nunique()} unique venues")

# ---- STEP 2: Fix team names ----
team_map = {
    "Delhi Daredevils"              : "Delhi Capitals",
    "Kings XI Punjab"               : "Punjab Kings",
    "Royal Challengers Bangalore"   : "Royal Challengers Bengaluru",
}
for col in ["batting_team", "bowling_team"]:
    deliveries[col] = deliveries[col].replace(team_map)
print("Team names standardised")

# ---- STEP 3: Flag extras properly ----
deliveries["is_wide"]   = deliveries["wides"].notna() & (deliveries["wides"] > 0)
deliveries["is_noball"] = deliveries["noballs"].notna() & (deliveries["noballs"] > 0)
deliveries["is_legal"]  = ~deliveries["is_wide"] & ~deliveries["is_noball"]
print(f"Legal deliveries: {deliveries['is_legal'].sum():,}")
print(f"Wides:            {deliveries['is_wide'].sum():,}")
print(f"No balls:         {deliveries['is_noball'].sum():,}")

# ---- STEP 4: Handle missing values ----
deliveries["runs_off_bat"] = deliveries["runs_off_bat"].fillna(0)
deliveries["extras"]       = deliveries["extras"].fillna(0)
deliveries["wicket_type"]  = deliveries["wicket_type"].fillna("not_out")
deliveries["bowler"]       = deliveries["bowler"].fillna("unknown")
print("Missing values handled")

# ---- STEP 5: Save as Parquet ----
output_path = r"C:\Projects\cricket\data"
os.makedirs(output_path, exist_ok=True)

deliveries.to_parquet(f"{output_path}\\deliveries_clean.parquet", index=False)
info.to_parquet(f"{output_path}\\info_clean.parquet", index=False)

print()
print("=== SAVED SUCCESSFULLY ===")
print(f"deliveries_clean.parquet — {len(deliveries):,} rows")
print(f"info_clean.parquet       — {len(info):,} rows")
print(f"Location: {output_path}")