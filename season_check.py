import pandas as pd
import os

ipl_path = r"C:\Projects\cricket\ipl"
all_info = []

for filename in os.listdir(ipl_path):
    filepath = os.path.join(ipl_path, filename)
    if filename.endswith("_info.csv"):
        df = pd.read_csv(filepath, header=None, names=["type", "key", "value"], on_bad_lines='skip')
        df["match_id"] = filename.replace("_info.csv", "")
        all_info.append(df)

info = pd.concat(all_info, ignore_index=True)

def get_value(info_df, key):
    return info_df[info_df["key"] == key][["match_id", "value"]].rename(columns={"value": key})

seasons  = get_value(info, "season")
toss_dec = get_value(info, "toss_decision")
toss_win = get_value(info, "toss_winner")
winner   = get_value(info, "winner")

matches = seasons.merge(toss_dec, on="match_id")
matches = matches.merge(toss_win, on="match_id")
matches = matches.merge(winner, on="match_id")

# Filter 2021 onwards
matches = matches[matches["season"].isin(["2021","2022","2023","2024","2025","2026"])]

# Chasing team won = toss winner chose field AND toss winner won
matches["chasing_won"] = matches.apply(
    lambda row: row["toss_winner"] == row["winner"] if row["toss_decision"] == "field"
    else row["toss_winner"] != row["winner"], axis=1
)

total        = len(matches)
chasing_wins = matches["chasing_won"].sum()
batting_wins = total - chasing_wins

print(f"=== CHASING vs BATTING FIRST (2021-2026) ===")
print()
print(f"Total matches  : {total}")
print(f"Chasing won    : {chasing_wins}  ({round(chasing_wins/total*100,1)}%)")
print(f"Batting first won : {batting_wins}  ({round(batting_wins/total*100,1)}%)")
print()
print("=== BY SEASON ===")
for season in ["2021","2022","2023","2024","2025","2026"]:
    s = matches[matches["season"] == season]
    cw = s["chasing_won"].sum()
    t  = len(s)
    print(f"{season}: {t} matches | Chasing won {cw} ({round(cw/t*100,1)}%)")