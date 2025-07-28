import pandas as pd
from tvi_footballindex.utils import helpers

def calculate_tvi(
    all_metric_events,
    player_playtime,
    C=90/44,
    grid_shape=(3, 3),
    zone_map=[2, 1, 2, 4, 3, 4, 6, 5, 6]
):
    """
    Calculate the Total Value Index (TVI) for players based on pre-calculated metric events and playtime.

    Args:
        all_metric_events (pd.DataFrame): DataFrame containing player actions with x and y coordinates.
                                          Expected columns: ['game_id', 'team_id', 'player_id', 'event_name', 'x', 'y'].
        player_playtime (pd.DataFrame): DataFrame with columns ['game_id', 'team_id', 'player_id', 'play_time'].
        C (float, optional): Scaling constant for TVI calculation. Defaults to 90/44.
        grid_shape (tuple, optional): The shape of the grid as (rows, columns). Defaults to (3, 3).
        zone_map (list, optional): A list that maps the grid index to a specific zone number. The length of the list
                                   must be equal to rows * columns. Defaults to [2, 1, 2, 4, 3, 4, 6, 5, 6].

    Returns:
        pd.DataFrame: DataFrame with TVI and action diversity for each player.
    """
    # Assign zones to each event
    all_metric_events['zone'] = all_metric_events.apply(
        lambda row: helpers.assign_zones(row['x'], row['y'], grid_shape=grid_shape, zone_map=zone_map), axis=1
    )

    # Group by event type and zone
    all_metric_events = all_metric_events.groupby(
        ['game_id', 'team_id', 'player_id', 'event_name', 'zone']
    ).size().reset_index(name='count')

    # Pivot the data to have one row per player per match, with action counts as columns
    all_metric_events['event_zone'] = all_metric_events['event_name'] + '_' + all_metric_events['zone'].astype(str)
    tvi = all_metric_events.pivot_table(
        index=['game_id', 'team_id', 'player_id'],
        columns=['event_zone'],
        values='count'
    ).fillna(0).reset_index()

    # Calculate action diversity (number of unique action types performed)
    event_zone_cols = [col for col in tvi.columns if col not in ['game_id', 'team_id', 'player_id']]
    tvi['action_diversity'] = tvi[event_zone_cols].clip(upper=1).sum(axis=1)

    # Merge with playtime data
    tvi = pd.merge(tvi, player_playtime, on=['game_id', 'team_id', 'player_id'], how='right').fillna(0)

    # Calculate TVI score
    tvi['TVI'] = C * tvi['action_diversity'] / tvi['play_time']
    tvi['TVI'] = tvi['TVI'].clip(upper=1)

    return tvi


def aggregate_tvi_by_player(tvi_df):
    """
    Aggregates TVI (Total Value Index) metrics by player from a DataFrame containing per-match or per-event football statistics.
    This function processes the input DataFrame by:
    - Summing up defensive, progressive, and offensive actions for each of six pitch zones.
    - Ensuring all expected action columns exist, filling missing ones with zeros.
    - Dropping the original action columns after aggregation.
    - Grouping the data by player and computing a weighted average of the metrics using play time as the weight.
    - Merging the total play time per player.
    - Reordering and selecting relevant columns for the final output.
    Args:
        tvi_df (pd.DataFrame): Input DataFrame with columns for player actions per zone, 'player_id', 'team_id', 'game_id', 'play_time', 'action_diversity', and 'TVI'.
    Returns:
        pd.DataFrame: Aggregated DataFrame with one row per player, including summed and weighted metrics, sorted by 'TVI' in descending order.
    Notes:
        - Requires the 'helpers.weighted_avg' function to be defined elsewhere.
        - Assumes the presence of pandas as pd.
    """
    tvi_final = tvi_df.copy()
    columns_to_order = []
    for zone in range(1, 13):
        def_cols = [f'Aerial_{zone}', f'Interception_{zone}', f'Tackle_{zone}']
        prog_cols = [f'Take On_{zone}', f'progressive_pass_{zone}']
        off_cols = [f'deep_completition_{zone}', f'key_pass_{zone}', f'shots_on_target_{zone}']

        for col in def_cols + prog_cols + off_cols:
            if col not in tvi_final.columns:
                tvi_final[col] = 0

        tvi_final[f'defensive_zone_{zone}'] = tvi_final[def_cols].sum(axis=1)
        tvi_final[f'progressive_zone_{zone}'] = tvi_final[prog_cols].sum(axis=1)
        tvi_final[f'offensive_zone_{zone}'] = tvi_final[off_cols].sum(axis=1)

        tvi_final.drop(columns=def_cols + prog_cols + off_cols, inplace=True)
        columns_to_order.extend([f'defensive_zone_{zone}', f'progressive_zone_{zone}', f'offensive_zone_{zone}'])

    tvi_final = tvi_final.drop(columns=['team_id', 'game_id'])\
        .groupby('player_id').apply(helpers.weighted_avg, weight_column='play_time').reset_index()

    total_play_time = tvi_df.groupby('player_id')['play_time'].sum().reset_index()
    tvi_final = pd.merge(tvi_final, total_play_time, on='player_id', how='left')

    tvi_final = tvi_final[['player_id', 'action_diversity', 'play_time', 'TVI'] + columns_to_order]

    return tvi_final.sort_values('TVI', ascending=False)