import pandas as pd
from tvi_footballindex.utils import helpers

def calculate_tvi(
    events_df,
    playtime_df,
    player_id_col='player_id',
    event_name_col='event_name',
    x_col='x',
    y_col='y',
    game_id_col='game_id',
    team_id_col='team_id',
    playtime_col='play_time',
    C=90/44,
    zone_map=[[2, 4, 6],
              [1, 3, 5], 
              [2, 4, 6]]
):
    """
    Calculate the Tactical Versatility Index (TVI) for players based on their actions and playtime.
    
    TVI measures player versatility by analyzing action diversity across different pitch zones,
    normalized by playing time.

    Args:
        events_df (pd.DataFrame): DataFrame containing player actions with coordinates.
            Required columns: player_id, event_name, x, y, game_id, team_id
        playtime_df (pd.DataFrame): DataFrame with player playtime information.
            Required columns: player_id, play_time, game_id, team_id
        player_id_col (str, optional): Column name for player IDs. Defaults to 'player_id'.
        event_name_col (str, optional): Column name for event types. Defaults to 'event_name'.
        x_col (str, optional): Column name for x-coordinate (0-100 scale). Defaults to 'x'.
        y_col (str, optional): Column name for y-coordinate (0-100 scale). Defaults to 'y'.
        game_id_col (str, optional): Column name for game IDs. Defaults to 'game_id'.
        team_id_col (str, optional): Column name for team IDs. Defaults to 'team_id'.
        playtime_col (str, optional): Column name for playing time in minutes. Defaults to 'play_time'.
        C (float, optional): Scaling constant for TVI calculation. Higher values increase scores.
            Defaults to 90/44 ≈ 2.05.
        zone_map (list, optional): 2D list defining pitch zones. If None, uses default 3x3 grid.

    Returns:
        pd.DataFrame: DataFrame with TVI scores and metrics for each player-game combination.
            Key columns:
            - action_diversity: Number of unique action-zone combinations
            - TVI: Main versatility score (0-1, higher = more versatile)
            - TVI_entropy: Alternative entropy-based score
            - shannon_entropy: Raw entropy of action distribution

    Raises:
        KeyError: If required columns are missing from input DataFrames.
        ValueError: If DataFrames are empty or contain invalid data.

    Example:
        >>> events = pd.DataFrame({
        ...     'player_id': [1, 1, 2],
        ...     'event_name': ['pass', 'shot', 'tackle'],
        ...     'x': [30, 70, 20], 'y': [50, 60, 40],
        ...     'game_id': [1, 1, 1], 'team_id': [101, 101, 102]
        ... })
        >>> playtime = pd.DataFrame({
        ...     'player_id': [1, 2], 'play_time': [90, 75],
        ...     'game_id': [1, 1], 'team_id': [101, 102]
        ... })
        >>> tvi_df = calculate_tvi(events, playtime)
    """
    # Input validation
    if events_df.empty:
        raise ValueError("events_df cannot be empty")
    if playtime_df.empty:
        raise ValueError("playtime_df cannot be empty")
    
    # Check required columns
    required_event_cols = [player_id_col, event_name_col, x_col, y_col, game_id_col, team_id_col]
    required_playtime_cols = [player_id_col, playtime_col, game_id_col, team_id_col]
    
    missing_event_cols = [col for col in required_event_cols if col not in events_df.columns]
    missing_playtime_cols = [col for col in required_playtime_cols if col not in playtime_df.columns]
    
    if missing_event_cols:
        raise KeyError(f"Missing columns in events_df: {missing_event_cols}")
    if missing_playtime_cols:
        raise KeyError(f"Missing columns in playtime_df: {missing_playtime_cols}")

    # Use default zone map if none provided
    if zone_map is None:
        zone_map = [
            [2, 4, 6],
            [1, 3, 5], 
            [2, 4, 6]
        ]

    # Work with copies to avoid modifying originals
    events = events_df.copy()
    playtime = playtime_df.copy()

    # Assign zones to each event
    events['zone'] = events.apply(
        lambda row: helpers.assign_zones(row[x_col], row[y_col], zone_map=zone_map), 
        axis=1
    )

    # Group by event type and zone to count occurrences
    events_grouped = events.groupby(
        [game_id_col, team_id_col, player_id_col, event_name_col, 'zone']
    ).size().reset_index(name='count')

    # Create event-zone combinations
    events_grouped['event_zone'] = (
        events_grouped[event_name_col] + '_' + events_grouped['zone'].astype(str)
    )
    
    # Pivot to get event-zone columns
    tvi = events_grouped.pivot_table(
        index=[game_id_col, team_id_col, player_id_col],
        columns=['event_zone'],
        values='count'
    ).fillna(0).reset_index()

    # Calculate action diversity (number of unique action-zone combinations)
    event_zone_cols = [col for col in tvi.columns 
                       if col not in [game_id_col, team_id_col, player_id_col]]
    tvi['action_diversity'] = tvi[event_zone_cols].clip(upper=1).sum(axis=1)

    # Calculate Shannon entropy for alternative TVI measure
    def calculate_player_entropy(row):
        counts = row[event_zone_cols].values
        return helpers.calculate_shannon_entropy(counts)
    
    tvi['shannon_entropy'] = tvi.apply(calculate_player_entropy, axis=1)

    # Merge with playtime data (right join to include all players with playtime)
    tvi = pd.merge(
        tvi, playtime, 
        on=[game_id_col, team_id_col, player_id_col], 
        how='right'
    ).fillna(0)

    # Calculate TVI scores
    # Avoid division by zero
    valid_playtime = tvi[playtime_col] > 0
    
    tvi['TVI_entropy'] = 0.0
    tvi.loc[valid_playtime, 'TVI_entropy'] = (
        tvi.loc[valid_playtime, 'shannon_entropy'] / tvi.loc[valid_playtime, playtime_col]
    )
    tvi['TVI_entropy'] = tvi['TVI_entropy'].clip(upper=1)
    
    tvi['TVI'] = 0.0
    tvi.loc[valid_playtime, 'TVI'] = (
        C * tvi.loc[valid_playtime, 'action_diversity'] / tvi.loc[valid_playtime, playtime_col]
    )
    tvi['TVI'] = tvi['TVI'].clip(upper=1)

    return tvi


def aggregate_tvi_by_player(
    tvi_df,
    player_id_col='player_id',
    playtime_col='play_time',
    position_col='position'
):
    """
    Aggregate TVI metrics by player across all games.
    
    Uses weighted averages based on playing time to provide season-level statistics.

    Args:
        tvi_df (pd.DataFrame): Output from calculate_tvi() function.
        player_id_col (str, optional): Column name for player IDs. Defaults to 'player_id'.
        playtime_col (str, optional): Column name for playtime. Defaults to 'play_time'.
        position_col (str, optional): Column name for positions. Defaults to 'position'.
            If column doesn't exist, this parameter is ignored.

    Returns:
        pd.DataFrame: Aggregated DataFrame with one row per player, sorted by TVI descending.
            Includes weighted averages of all metrics and total playing time.

    Raises:
        KeyError: If required columns are missing.
        ValueError: If input DataFrame is empty.

    Example:
        >>> game_tvi = calculate_tvi(events_df, playtime_df)
        >>> player_tvi = aggregate_tvi_by_player(game_tvi)
        >>> print(player_tvi[['player_id', 'TVI', 'total_play_time']].head())
    """
    if tvi_df.empty:
        raise ValueError("tvi_df cannot be empty")
    
    if player_id_col not in tvi_df.columns:
        raise KeyError(f"Column '{player_id_col}' not found in tvi_df")
    if playtime_col not in tvi_df.columns:
        raise KeyError(f"Column '{playtime_col}' not found in tvi_df")

    tvi_final = tvi_df.copy()

    # Check if position column exists
    has_position = position_col in tvi_final.columns
    
    # Columns to drop before aggregation
    cols_to_drop = ['team_id', 'game_id']
    if has_position:
        cols_to_drop.append(position_col)
    
    # Only drop columns that exist
    cols_to_drop = [col for col in cols_to_drop if col in tvi_final.columns]
    
    # Weighted average of metrics
    tvi_aggregated = (tvi_final.drop(columns=cols_to_drop)
                     .groupby([player_id_col])
                     .apply(helpers.weighted_avg, weight_column=playtime_col)
                     .reset_index())
    
    # Handle position data if available
    if has_position:
        # Find most played position
        position_time = (tvi_df.groupby([player_id_col, position_col])[playtime_col]
                        .sum().reset_index())
        most_played_position = position_time.loc[
            position_time.groupby(player_id_col)[playtime_col].idxmax()
        ][[player_id_col, position_col]].rename(columns={position_col: 'main_position'})
        
        # Merge position data
        tvi_aggregated = pd.merge(
            tvi_aggregated, most_played_position, 
            on=[player_id_col], how='left'
        )

    # Calculate total playtime
    total_play_time = (tvi_df.groupby([player_id_col])[playtime_col]
                      .sum().reset_index()
                      .rename(columns={playtime_col: 'total_play_time'}))

    # Merge total playtime
    tvi_aggregated = pd.merge(
        tvi_aggregated, total_play_time, 
        on=[player_id_col], how='left'
    )

    # Final adjustments
    tvi_aggregated[playtime_col] = tvi_aggregated['total_play_time']
    tvi_aggregated = tvi_aggregated.drop(columns=['total_play_time'])
    
    if has_position:
        tvi_aggregated = tvi_aggregated.rename(columns={'main_position': position_col})

    return tvi_aggregated.sort_values('TVI', ascending=False)


def validate_data_format(events_df, playtime_df, **kwargs):
    """
    Validate input data format and provide helpful error messages.
    
    Args:
        events_df (pd.DataFrame): Events DataFrame to validate
        playtime_df (pd.DataFrame): Playtime DataFrame to validate
        **kwargs: Column name parameters (same as calculate_tvi)
    
    Returns:
        dict: Validation results with 'valid' (bool) and 'messages' (list)
    
    Example:
        >>> result = validate_data_format(events_df, playtime_df)
        >>> if not result['valid']:
        ...     for msg in result['messages']:
        ...         print(f"⚠️  {msg}")
    """
    messages = []
    valid = True
    
    # Extract column names
    player_id_col = kwargs.get('player_id_col', 'player_id')
    event_name_col = kwargs.get('event_name_col', 'event_name')
    x_col = kwargs.get('x_col', 'x')
    y_col = kwargs.get('y_col', 'y')
    game_id_col = kwargs.get('game_id_col', 'game_id')
    team_id_col = kwargs.get('team_id_col', 'team_id')
    playtime_col = kwargs.get('playtime_col', 'play_time')
    
    # Check DataFrame existence and emptiness
    if events_df is None or events_df.empty:
        messages.append("events_df is empty or None")
        valid = False
    if playtime_df is None or playtime_df.empty:
        messages.append("playtime_df is empty or None")
        valid = False
        
    if not valid:
        return {'valid': False, 'messages': messages}
    
    # Check required columns
    required_event_cols = [player_id_col, event_name_col, x_col, y_col, game_id_col, team_id_col]
    required_playtime_cols = [player_id_col, playtime_col, game_id_col, team_id_col]
    
    missing_event_cols = [col for col in required_event_cols if col not in events_df.columns]
    missing_playtime_cols = [col for col in required_playtime_cols if col not in playtime_df.columns]
    
    if missing_event_cols:
        messages.append(f"Missing columns in events_df: {missing_event_cols}")
        messages.append(f"Available columns: {list(events_df.columns)}")
        valid = False
        
    if missing_playtime_cols:
        messages.append(f"Missing columns in playtime_df: {missing_playtime_cols}")
        messages.append(f"Available columns: {list(playtime_df.columns)}")
        valid = False
    
    if not valid:
        return {'valid': False, 'messages': messages}
    
    # Check coordinate ranges
    x_vals = events_df[x_col].dropna()
    y_vals = events_df[y_col].dropna()
    
    if len(x_vals) > 0:
        if x_vals.min() < 0 or x_vals.max() > 100:
            messages.append(f"x coordinates should be 0-100, found range: {x_vals.min():.1f} to {x_vals.max():.1f}")
    
    if len(y_vals) > 0:
        if y_vals.min() < 0 or y_vals.max() > 100:
            messages.append(f"y coordinates should be 0-100, found range: {y_vals.min():.1f} to {y_vals.max():.1f}")
    
    # Check for null values in key columns
    null_checks = [
        (events_df[player_id_col].isnull().sum(), f"events_df.{player_id_col}"),
        (events_df[event_name_col].isnull().sum(), f"events_df.{event_name_col}"),
        (playtime_df[player_id_col].isnull().sum(), f"playtime_df.{player_id_col}"),
        (playtime_df[playtime_col].isnull().sum(), f"playtime_df.{playtime_col}")
    ]
    
    for null_count, col_name in null_checks:
        if null_count > 0:
            messages.append(f"Found {null_count} null values in {col_name}")
    
    # Check playtime values
    playtime_vals = playtime_df[playtime_col].dropna()
    if len(playtime_vals) > 0:
        if playtime_vals.min() <= 0:
            messages.append(f"All playtime values should be positive, found minimum: {playtime_vals.min()}")
        if playtime_vals.max() > 120:
            messages.append(f"Playtime values seem high (>120 min), maximum found: {playtime_vals.max()}")
    
    # Success message if all good
    if not messages:
        messages.append("✅ Data format validation passed!")
    
    return {'valid': len([m for m in messages if not m.startswith('✅')]) == 0, 'messages': messages}