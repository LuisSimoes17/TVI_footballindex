import pandas as pd
from tvi_footballindex.parsing import f24_parser
from tvi_footballindex.tvi import calculator

# Define paths
F24_FOLDER_PATH = "examples/data/F24 - Portugal"
PLAYER_NAME_PATH = "examples/data/opta_planteis_portugal.xlsx"

# 1. Parse F24 data
print("Parsing F24 data...")
event_df = f24_parser.parsef24_folder(F24_FOLDER_PATH)

# 2. Calculate player playtime
print("Calculating player playtime...")
play_time = f24_parser.calculate_player_playtime(event_df, min_playtime=30)

# Defensive Actions
interceptions = f24_parser.get_interceptions(event_df)
tackles = f24_parser.get_tackles(event_df)
aerials = f24_parser.get_aerials(event_df)

# Possession Actions
progressive_passes = f24_parser.get_progressive_passes(event_df)
dribbles = f24_parser.get_dribbles(event_df)

# Offensive Actions
key_passes = f24_parser.get_key_passes(event_df)
deep_completions = f24_parser.get_deep_completions(event_df)
shots_on_target = f24_parser.get_shots_on_target(event_df)

# Combine all actions into a single DataFrame
all_metric_events = pd.concat([
    interceptions, tackles, aerials, progressive_passes, dribbles, key_passes, deep_completions, shots_on_target
])

# Calculate TVI
tvi_df = calculator.calculate_tvi(
    events_df=all_metric_events, 
    playtime_df=play_time
)

# Aggregate TVI by player
aggregated_tvi = calculator.aggregate_tvi_by_player(tvi_df)

# 5. Add player names and filter
print("Adding player names and filtering...")
player_names = pd.read_excel(PLAYER_NAME_PATH).drop(columns=['position']).drop_duplicates()
aggregated_tvi['player_id'] = aggregated_tvi['player_id'].astype('int')
tvi_final = pd.merge(player_names, aggregated_tvi, on='player_id', how='right')

# Filter out goalkeepers and players with low playtime
tvi_final = tvi_final[tvi_final['position'] != 'Goalkeeper']
tvi_final_filtered = tvi_final[tvi_final['play_time'] > 450].sort_values('TVI', ascending=False).reset_index(drop=True)

# 6. Display results
print("\n--- Top 20 Players by TVI ---")
print(tvi_final_filtered.head(20))