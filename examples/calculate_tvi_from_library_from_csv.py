import pandas as pd
from tvi_footballindex.parsing import f24_parser
from tvi_footballindex.tvi import calculator

# Define paths
file_name = "ENG-Premier League_24-25"
f24_file_path = f"examples/data/F24 - CSVs/{file_name}_events.csv"

# 1. Parse F24 data
print("Parsing F24 data...")
event_df = f24_parser.parsef24_csv(f24_file_path)

# 2. Calculate player playtime
print("Calculating player playtime...")
play_time = f24_parser.calculate_player_playtime(event_df, min_playtime=30, from_processed=True)

# Defensive Actions
interceptions = f24_parser.get_interceptions(event_df, from_processed=True)
tackles = f24_parser.get_tackles(event_df, from_processed=True)
aerials = f24_parser.get_aerials(event_df, from_processed=True)

# Possession Actions
progressive_passes = f24_parser.get_progressive_passes(event_df, from_processed=True)
dribbles = f24_parser.get_dribbles(event_df, from_processed=True)

# Offensive Actions
key_passes = f24_parser.get_key_passes(event_df, from_processed=True)
deep_completions = f24_parser.get_deep_completions(event_df, from_processed=True)
shots_on_target = f24_parser.get_shots_on_target(event_df, from_processed=True)

# Combine all actions into a single DataFrame
all_metric_events = pd.concat([
    interceptions, tackles, aerials, progressive_passes, dribbles, key_passes, deep_completions, shots_on_target
])
all_metric_events['player_id'] = all_metric_events['player_id'].astype(int).astype(str)

# Calculate TVI with the custom grid
tvi_df = calculator.calculate_tvi(
    all_metric_events, 
    play_time
)

# Aggregate TVI by player
aggregated_tvi = calculator.aggregate_tvi_by_player(tvi_df)

# 5. Add player names and filter
print("Adding player names and filtering...")
player_names = (
    event_df[["player_id", "player", "team_id", "team"]].drop_duplicates().dropna()
)
player_names.rename(
    columns={"player": "player_name", "team": "team_name"}, inplace=True
)
aggregated_tvi['player_id'] = aggregated_tvi['player_id'].astype(int)
tvi_final = pd.merge(player_names, aggregated_tvi, on='player_id', how='right')

# write the final DataFrame to a CSV file
tvi_final.sort_values('TVI', ascending=False).to_csv(f"./examples/data/output/{file_name}_TVI.csv", index=False)

# Filter out goalkeepers and players with low playtime
tvi_final = tvi_final[tvi_final['position'] != 'Goalkeeper']
tvi_final_filtered = tvi_final[tvi_final['play_time'] > 450].sort_values('TVI', ascending=False).reset_index(drop=True)

# 6. Display results
print("\n--- Top 20 Players by TVI ---")
print(tvi_final_filtered.head(20))
