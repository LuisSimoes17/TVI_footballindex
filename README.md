# TVI Football Index

[![PyPI version](https://badge.fury.io/py/tvi-footballindex.svg)](https://badge.fury.io/py/tvi-footballindex)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project provides a Python library for calculating the **Tactical Versatility Index (TVI)**, a metric designed to quantify a player's ability to perform various actions across different zones of the football pitch. The library is built to be flexible and customizable, allowing for in-depth analysis of player performance.

## Key Features

- **Flexible TVI Calculator**: The core of the library, designed to work with any data source.
- **Customizable Zone Grid**: Define your own pitch zones for tailored analysis.
- **Pandas Integration**: Built on top of pandas for seamless data manipulation.
- **Wyscout F24 Parser**: A convenience module for parsing F24 XML data.

## Installation

You can install the TVI Football Index library directly from PyPI:

```bash
pip install tvi-footballindex
```

## Quick Start with Custom Data

The main strength of this library is its ability to calculate the TVI from any events DataFrame. Here's how you can use it with your own data:

```python
import pandas as pd
from tvi_footballindex.tvi import calculator

# Assume you have a DataFrame with event data and another with playtime data
# events_df should have columns for player_id, event_name, x, and y
# playtime_df should have columns for player_id and play_time

# Sample DataFrames (replace with your actual data)
events_data = {
    'player_id': [1, 1, 2, 2, 1],
    'event_name': ['pass', 'dribble', 'shot', 'pass', 'tackle'],
    'x': [50, 60, 80, 70, 20],
    'y': [50, 40, 60, 30, 50],
    'game_id': [1, 1, 1, 1, 1],
    'team_id': [101, 101, 102, 102, 101]
}
events_df = pd.DataFrame(events_data)

playtime_data = {
    'player_id': [1, 2],
    'play_time': [90, 90],
    'game_id': [1, 1],
    'team_id': [101, 102]
}
playtime_df = pd.DataFrame(playtime_data)

# Calculate TVI
tvi_df = calculator.calculate_tvi(events_df, playtime_df)

# Aggregate TVI by player
aggregated_tvi = calculator.aggregate_tvi_by_player(tvi_df)

# Display results
print(aggregated_tvi)
```

## Parsing F24 Data (Optional)

If you work with Wyscout F24 data, you can use the parsing module to extract the necessary information.

```python
import pandas as pd
from tvi_footballindex.parsing import f24_parser
from tvi_footballindex.tvi import calculator

# Define paths
F24_FOLDER_PATH = "path/to/your/F24_folder"

# 1. Parse F24 data
event_df = f24_parser.parsef24_folder(F24_FOLDER_PATH)

# 2. Calculate player playtime
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

# 7. Display results
print(aggregated_tvi.head(20))
```

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.