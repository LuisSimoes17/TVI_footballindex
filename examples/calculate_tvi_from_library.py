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
play_time = f24_parser.calculate_player_playtime(match_events, min_playtime=30)

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

# Define a 4x3 grid and a corresponding zone map
grid_shape = (4, 3)
zone_map = [
    1, 2, 3,  # Row 1
    4, 5, 6,  # Row 2
    7, 8, 9,  # Row 3
    10, 11, 12 # Row 4
]

# Calculate TVI with the custom grid
tvi_df = calculator.calculate_tvi(
    all_metric_events, 
    play_time, 
    grid_shape=grid_shape, 
    zone_map=zone_map
)

# Aggregate TVI by player
aggregated_tvi = calculator.aggregate_tvi_by_player(tvi_df)

print(aggregated_tvi)