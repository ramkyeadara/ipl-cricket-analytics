import pandas as pd
import os

# Path to your IPL folder
ipl_path = r"C:\Projects\cricket\ipl"

# Empty lists to collect all matches
all_deliveries = []
all_info = []

# Loop through every file in the folder
for filename in os.listdir(ipl_path):
    filepath = os.path.join(ipl_path, filename)
    
    # Info files
    if filename.endswith("_info.csv"):
        df = pd.read_csv(filepath, header=None, names=["type", "key", "value"], on_bad_lines='skip')
        df["match_id"] = filename.replace("_info.csv", "")
        all_info.append(df)
    
    # Delivery files
    elif filename.endswith(".csv") and "_info" not in filename:
        df = pd.read_csv(filepath)
        df["match_id"] = filename.replace(".csv", "")
        all_deliveries.append(df)

# Combine everything
deliveries = pd.concat(all_deliveries, ignore_index=True)
info = pd.concat(all_info, ignore_index=True)

# What do we have?
print("=== DELIVERIES ===")
print(f"Total balls: {len(deliveries):,}")
print(f"Columns: {list(deliveries.columns)}")
print()
print(deliveries.head(3))

print()
print("=== INFO ===")
print(f"Total matches: {info['match_id'].nunique():,}")
print()
print(info.head(20))


print()
print("=== TOP 10 RUN SCORERS - ALL IPL ===")
top_batters = deliveries.groupby("striker")["runs_off_bat"].sum().sort_values(ascending=False).head(10)
print(top_batters)