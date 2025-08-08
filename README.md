# TVI Football Index

[![PyPI version](https://badge.fury.io/py/tvi-footballindex.svg)](https://badge.fury.io/py/tvi-footballindex) 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project provides a Python library for calculating the **Tactical Versatility Index (TVI)**, a metric designed to quantify a player's ability to perform various actions across different zones of the football pitch, assessing the versatility of the player. The library is built to be flexible and customizable, allowing for in-depth analysis of player performance.

## Key Features

- **F24 Parser**: A module to parse and process F24 XML data from Wyscout.
- **TVI Calculator**: A module to calculate the TVI for players based on their in-game actions.
- **Customizable Zone Grid**: The flexibility to define custom pitch zones for analysis.
- **Pandas Integration**: Built on top of pandas for seamless data manipulation and analysis.

## Installation

You can install the TVI Football Index library directly from PyPI:

```bash
pip install tvi-footballindex
```

## Quick Start

The following example demonstrates how to use the library to calculate the TVI for players from a folder of F24 XML files.

```python
import pandas as pd
from tvi_footballindex.parsing import f24_parser
from tvi_footballindex.tvi import calculator

# Define paths
F24_FOLDER_PATH = "path/to/your/F24_folder"
PLAYER_NAME_PATH = "path/to/your/player_names.xlsx"

# 1. Parse F24 data
print("Parsing F24 data...")
event_df = f24_parser.parsef24_folder(F24_FOLDER_PATH)

# 2. Calculate player playtime
print("Calculating player playtime...")
play_time = f24_parser.calculate_player_playtime(event_df, min_playtime=30)

# 3. Get all relevant actions
interceptions = f24_parser.get_interceptions(event_df)
tackles = f24_parser.get_tackles(event_df)
aerials = f24_parser.get_aerials(event_df)
progressive_passes = f24_parser.get_progressive_passes(event_df)
dribbles = f24_parser.get_dribbles(event_df)
key_passes = f24_parser.get_key_passes(event_df)
deep_completions = f24_parser.get_deep_completions(event_df)
shots_on_target = f24_parser.get_shots_on_target(event_df)

# 4. Combine all actions into a single DataFrame
all_metric_events = pd.concat([
    interceptions, tackles, aerials, progressive_passes, dribbles, key_passes, deep_completions, shots_on_target
])

# 5. Calculate TVI
tvi_df = calculator.calculate_tvi(all_metric_events, play_time)

# 6. Aggregate TVI by player
aggregated_tvi = calculator.aggregate_tvi_by_player(tvi_df)

# 7. Add player names and filter
print("Adding player names and filtering...")
player_names = pd.read_excel(PLAYER_NAME_PATH).drop(columns=['position']).drop_duplicates()
aggregated_tvi['player_id'] = aggregated_tvi['player_id'].astype('int')
tvi_final = pd.merge(player_names, aggregated_tvi, on='player_id', how='right')

# Filter out goalkeepers and players with low playtime
tvi_final = tvi_final[tvi_final['position'] != 'Goalkeeper']
tvi_final_filtered = tvi_final[tvi_final['play_time'] > 450].sort_values('TVI', ascending=False).reset_index(drop=True)

# 8. Display results
print("\n--- Top 20 Players by TVI ---")
print(tvi_final_filtered.head(20))
```

For more detailed examples, please refer to the `examples` folder in the repository.

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
