# TVI Football Index

[![PyPI version](https://badge.fury.io/py/tvi-footballindex.svg)](https://badge.fury.io/py/tvi-footballindex)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for calculating the **Tactical Versatility Index (TVI)**, a metric that quantifies a player's ability to perform various actions across different zones of the football pitch. TVI measures how versatile a player is by analyzing their action diversity and spatial coverage.

## What is TVI?

The Tactical Versatility Index measures player versatility by:
- **Action Diversity**: How many different types of actions a player performs
- **Spatial Coverage**: How many different pitch zones a player is active in
- **Time Normalization**: Adjusting for actual playing time

Higher TVI scores indicate more versatile players who contribute across multiple areas and action types.

## Installation

```bash
pip install tvi-footballindex
```

## Quick Start

### Basic Example with Sample Data

```python
import pandas as pd
from tvi_footballindex.tvi.calculator import calculate_tvi, aggregate_tvi_by_player

# Create sample event data
events_df = pd.DataFrame({
    'player_id': [1, 1, 2, 2, 1, 2],
    'event_name': ['pass', 'dribble', 'shot', 'pass', 'tackle', 'interception'],
    'x': [30, 60, 80, 70, 20, 40],  # x-coordinate (0-100)
    'y': [50, 40, 60, 30, 50, 20],  # y-coordinate (0-100)
    'game_id': [1, 1, 1, 1, 1, 1],
    'team_id': [101, 101, 102, 102, 101, 102]
})

# Create playtime data (in minutes)
playtime_df = pd.DataFrame({
    'player_id': [1, 2],
    'play_time': [90, 75],
    'game_id': [1, 1],
    'team_id': [101, 102]
})

# Calculate TVI
tvi_results = calculate_tvi(events_df, playtime_df)
print("Game-level TVI:")
print(tvi_results[['player_id', 'action_diversity', 'TVI']].head())

# Aggregate across all games for each player
player_tvi = aggregate_tvi_by_player(tvi_results)
print("\nPlayer-level TVI:")
print(player_tvi[['player_id', 'action_diversity', 'TVI']].head())
```

### Required Data Format

Your data needs two DataFrames:

**Events DataFrame** must contain:
- `player_id`: Unique player identifier
- `event_name`: Type of action (e.g., 'pass', 'shot', 'tackle')
- `x`, `y`: Coordinates on the pitch (0-100 scale recommended)
- `game_id`: Game identifier
- `team_id`: Team identifier

**Playtime DataFrame** must contain:
- `player_id`: Unique player identifier  
- `play_time`: Minutes played in the game
- `game_id`: Game identifier
- `team_id`: Team identifier

## Customization

### Custom Column Names

If your data uses different column names:

```python
tvi_results = calculate_tvi(
    events_df, 
    playtime_df,
    player_id_col='player_uuid',
    event_name_col='action_type',
    x_col='pos_x',
    y_col='pos_y'
)
```

### Custom Pitch Zones

The default creates a 3×3 grid (9 zones). You can customize this:

```python
# Create a 4×4 grid with 16 zones
custom_zones = [
    [1, 2, 3, 4],
    [5, 6, 7, 8], 
    [9, 10, 11, 12],
    [13, 14, 15, 16]
]

tvi_results = calculate_tvi(
    events_df, 
    playtime_df, 
    zone_map=custom_zones
)
```

### Scaling Factor

Adjust the TVI scaling constant (default is ~2.05):

```python
tvi_results = calculate_tvi(
    events_df, 
    playtime_df,
    C=3.0  # Higher values increase TVI scores
)
```

## Working with F24 Data

If you have Wyscout F24 XML files:

```python
from tvi_footballindex.parsing import f24_parser

# Parse F24 files from a folder
events_df = f24_parser.parsef24_folder("path/to/f24_folder")

# Calculate playtime (minimum 30 minutes to be included)
playtime_df = f24_parser.calculate_player_playtime(events_df, min_playtime=30)

# Extract specific action types
passes = f24_parser.get_progressive_passes(events_df)
dribbles = f24_parser.get_dribbles(events_df)
shots = f24_parser.get_shots_on_target(events_df)
# ... other action extractors available

# Combine all actions
all_actions = pd.concat([passes, dribbles, shots])

# Calculate TVI
tvi_results = calculate_tvi(all_actions, playtime_df)
```

## Understanding the Results

The main metrics returned are:

- **`action_diversity`**: Number of unique action-zone combinations
- **`TVI`**: Main versatility score (0-1, higher = more versatile)  
- **`TVI_entropy`**: Alternative entropy-based score (optional)
- **`shannon_entropy`**: Raw entropy of action distribution

## API Reference

### Core Functions

#### `calculate_tvi(events_df, playtime_df, **kwargs)`
Calculate TVI scores for each player in each game.

**Parameters:**
- `events_df` (DataFrame): Event data with coordinates
- `playtime_df` (DataFrame): Playing time data
- `player_id_col` (str): Column name for player IDs (default: 'player_id')
- `event_name_col` (str): Column name for event types (default: 'event_name') 
- `x_col`, `y_col` (str): Column names for coordinates (default: 'x', 'y')
- `C` (float): Scaling constant (default: 90/44 ≈ 2.05)
- `zone_map` (list): Grid defining pitch zones

**Returns:** DataFrame with TVI scores per player per game

#### `aggregate_tvi_by_player(tvi_df, **kwargs)`
Aggregate game-level TVI into player-level statistics.

**Parameters:**
- `tvi_df` (DataFrame): Output from `calculate_tvi()`
- `player_id_col` (str): Column name for player IDs
- `playtime_col` (str): Column name for playtime

**Returns:** DataFrame with aggregated TVI per player

## Examples and Use Cases

- **Squad Analysis**: Compare versatility across your team
- **Recruitment**: Identify versatile players in other teams  
- **Tactical Analysis**: Understand how formation changes affect versatility
- **Player Development**: Track versatility improvement over time

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see [LICENSE](LICENSE) file for details.