import pandas as pd
from tvi_footballindex.parsing import f24_parser
from tvi_footballindex.tvi import calculator

# Define paths
F24_FOLDER_PATH = "examples/data/F24 - Portugal"
PLAYER_NAME_PATH = "examples/data/opta_planteis_portugal.xlsx"

# 1. Parse F24 data
print("Parsing F24 data...")
match_events = f24_parser.parsef24_folder(F24_FOLDER_PATH)

# 2. Calculate player playtime
print("Calculating player playtime...")
play_time = f24_parser.calculate_player_playtime(match_events, min_playtime=30)

# 3. Calculate TVI per game
print("Calculating TVI for each game...")
tvi_per_game = calculator.calculate_tvi(match_events, play_time)

# 4. Aggregate TVI by player
print("Aggregating TVI by player...")
tvi_aggregated = calculator.aggregate_tvi_by_player(tvi_per_game)

# 5. Add player names and filter
print("Adding player names and filtering...")
player_names = pd.read_excel(PLAYER_NAME_PATH)
tvi_aggregated['player_id'] = tvi_aggregated['player_id'].astype('int')
tvi_final = pd.merge(player_names, tvi_aggregated, on='player_id', how='right')

# Filter out goalkeepers and players with low playtime
tvi_final = tvi_final[tvi_final['position'] != 'Goalkeeper']
tvi_final_filtered = tvi_final[tvi_final['play_time'] > 450].sort_values('TVI', ascending=False).reset_index(drop=True)

# 6. Display results
print("\n--- Top 20 Players by TVI ---")
print(tvi_final_filtered.head(20))
