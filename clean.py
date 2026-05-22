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
    # Chinnaswamy
    "M Chinnaswamy Stadium, Bengaluru"                                     : "M Chinnaswamy Stadium",
    "M.Chinnaswamy Stadium"                                                : "M Chinnaswamy Stadium",
    # Mohali
    "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh"    : "PCA Stadium Mohali",
    "Punjab Cricket Association Stadium, Mohali"                           : "PCA Stadium Mohali",
    "Punjab Cricket Association IS Bindra Stadium, Mohali"                 : "PCA Stadium Mohali",
    "Punjab Cricket Association IS Bindra Stadium"                         : "PCA Stadium Mohali",
    # Hyderabad
    "Rajiv Gandhi International Stadium, Uppal, Hyderabad"                 : "Rajiv Gandhi Stadium Hyderabad",
    "Rajiv Gandhi International Stadium, Uppal"                            : "Rajiv Gandhi Stadium Hyderabad",
    "Rajiv Gandhi International Stadium"                                   : "Rajiv Gandhi Stadium Hyderabad",
    # Wankhede
    "Wankhede Stadium, Mumbai"                                             : "Wankhede Stadium",
    # DY Patil
    "Dr DY Patil Sports Academy, Mumbai"                                   : "Dr DY Patil Sports Academy",
    # Visakhapatnam
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam"  : "ACA-VDCA Stadium Visakhapatnam",
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium"                 : "ACA-VDCA Stadium Visakhapatnam",
    # Ahmedabad
    "Narendra Modi Stadium, Ahmedabad"                                     : "Narendra Modi Stadium",
    "Sardar Patel Stadium, Motera"                                         : "Narendra Modi Stadium",
    # Delhi
    "Arun Jaitley Stadium, Delhi"                                          : "Arun Jaitley Stadium",
    "Feroz Shah Kotla"                                                     : "Arun Jaitley Stadium",
    # Kolkata
    "Eden Gardens, Kolkata"                                                : "Eden Gardens",
    # Chennai
    "MA Chidambaram Stadium, Chepauk, Chennai"                             : "MA Chidambaram Stadium",
    "MA Chidambaram Stadium, Chepauk"                                      : "MA Chidambaram Stadium",
    # Jaipur
    "Sawai Mansingh Stadium, Jaipur"                                       : "Sawai Mansingh Stadium",
    # Dharamsala
    "Himachal Pradesh Cricket Association Stadium, Dharamsala"             : "HPCA Stadium Dharamsala",
    "Himachal Pradesh Cricket Association Stadium"                         : "HPCA Stadium Dharamsala",
    # Chandigarh
    "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh" : "MYSI Stadium Chandigarh",
    "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur"   : "MYSI Stadium Chandigarh",
    # Pune
    "Maharashtra Cricket Association Stadium, Pune"                        : "Maharashtra Cricket Association Stadium",
    # Brabourne
    "Brabourne Stadium, Mumbai"                                            : "Brabourne Stadium",
    "Shaheed Veer Narayan Singh International Stadium, Raipur" : "Shaheed Veer Narayan Singh Stadium",
    "Shaheed Veer Narayan Singh International Stadium"         : "Shaheed Veer Narayan Singh Stadium",
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow" : "Ekana Cricket Stadium Lucknow",
}
deliveries["venue"] = deliveries["venue"].replace(venue_map)
print(f"Venues cleaned: {deliveries['venue'].nunique()} unique venues")

# ---- STEP 2: Fix team names ----
team_map = {
    "Delhi Daredevils"              : "Delhi Capitals",
    "Kings XI Punjab"               : "Punjab Kings",
    "Royal Challengers Bangalore"   : "Royal Challengers Bengaluru",
    "Rising Pune Supergiants"       : "Rising Pune Supergiant",
}
for col in ["batting_team", "bowling_team"]:
    deliveries[col] = deliveries[col].replace(team_map)
print("Team names standardised")

# ---- STEP 3: Fix season formats ----
season_map = {
    "2007/08" : "2008",
    "2009/10" : "2010",
    "2020/21" : "2020",
}
deliveries["season"] = deliveries["season"].replace(season_map)
info["value"]        = info["value"].replace(season_map)
print("Season formats fixed")

# ---- STEP 4: Flag extras properly ----
deliveries["is_wide"]   = deliveries["wides"].notna() & (deliveries["wides"] > 0)
deliveries["is_noball"] = deliveries["noballs"].notna() & (deliveries["noballs"] > 0)
deliveries["is_legal"]  = ~deliveries["is_wide"] & ~deliveries["is_noball"]
print(f"Legal deliveries: {deliveries['is_legal'].sum():,}")
print(f"Wides:            {deliveries['is_wide'].sum():,}")
print(f"No balls:         {deliveries['is_noball'].sum():,}")

# ---- STEP 5: Handle missing values ----
deliveries["runs_off_bat"] = deliveries["runs_off_bat"].fillna(0)
deliveries["extras"]       = deliveries["extras"].fillna(0)
deliveries["wicket_type"]  = deliveries["wicket_type"].fillna("not_out")
deliveries["bowler"]       = deliveries["bowler"].fillna("unknown")
print("Missing values handled")

# ---- STEP 6: Save as Parquet ----
output_path = r"C:\Projects\cricket\data"
os.makedirs(output_path, exist_ok=True)

deliveries.to_parquet(f"{output_path}\\deliveries_clean.parquet", index=False)
info.to_parquet(f"{output_path}\\info_clean.parquet", index=False)

print()
print("=== SAVED SUCCESSFULLY ===")
print(f"deliveries_clean.parquet - {len(deliveries):,} rows")
print(f"info_clean.parquet       - {len(info):,} rows")
print(f"Location: {output_path}")