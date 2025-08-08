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
    Calculate the Total Value Index (TVI) for players based on their on-field actions and playtime.

    This function is designed to be flexible and can work with any DataFrame as long as the required columns are specified.

    Args:
        events_df (pd.DataFrame): DataFrame containing player actions with x and y coordinates.
        playtime_df (pd.DataFrame): DataFrame with player playtime information.
        player_id_col (str, optional): Name of the column for player IDs. Defaults to 'player_id'.
        event_name_col (str, optional): Name of the column for event names. Defaults to 'event_name'.
        x_col (str, optional): Name of the column for the x-coordinate of the event. Defaults to 'x'.
        y_col (str, optional): Name of the column for the y-coordinate of the event. Defaults to 'y'.
        game_id_col (str, optional): Name of the column for game IDs. Defaults to 'game_id'.
        team_id_col (str, optional): Name of the column for team IDs. Defaults to 'team_id'.
        playtime_col (str, optional): Name of the column for playtime. Defaults to 'play_time'.
        C (float, optional): Scaling constant for TVI calculation. Defaults to 90/44.
        zone_map (list, optional): A list that maps the grid index to a specific zone number. 
                                   Defaults to a 3x3 grid.

    Returns:
        pd.DataFrame: DataFrame with TVI scores and other metrics for each player.
    """
    # Assign zones to each event
    events_df['zone'] = events_df.apply(
        lambda row: helpers.assign_zones(row[x_col], row[y_col], zone_map=zone_map), axis=1
    )

    # Group by event type and zone
    events_df = events_df.groupby(
        [game_id_col, team_id_col, player_id_col, event_name_col, 'zone']
    ).size().reset_index(name='count')

    # Pivot the data
    events_df['event_zone'] = events_df[event_name_col] + '_' + events_df['zone'].astype(str)
    tvi = events_df.pivot_table(
        index=[game_id_col, team_id_col, player_id_col],
        columns=['event_zone'],
        values='count'
    ).fillna(0).reset_index()

    # Calculate action diversity
    event_zone_cols = [col for col in tvi.columns if col not in [game_id_col, team_id_col, player_id_col]]
    tvi['action_diversity'] = tvi[event_zone_cols].clip(upper=1).sum(axis=1)

    # Calculate Shannon entropy
    def calculate_player_entropy(row):
        counts = row[event_zone_cols].values
        return helpers.calculate_shannon_entropy(counts)
    tvi['shannon_entropy'] = tvi.apply(calculate_player_entropy, axis=1)

    # Merge with playtime data
    tvi = pd.merge(tvi, playtime_df, on=[game_id_col, team_id_col, player_id_col], how='right').fillna(0)

    # Calculate TVI scores
    tvi['TVI_entropy'] = tvi['shannon_entropy'] / tvi[playtime_col]
    tvi['TVI_entropy'] = tvi['TVI_entropy'].clip(upper=1)
    tvi['TVI'] = C * tvi['action_diversity'] / tvi[playtime_col]
    tvi['TVI'] = tvi['TVI'].clip(upper=1)

    return tvi

def aggregate_tvi_by_player(
    tvi_df,
    player_id_col='player_id',
    playtime_col='play_time',
    position_col='position'
):
    """
    Aggregates TVI metrics by player.

    Args:
        tvi_df (pd.DataFrame): DataFrame with TVI scores from the calculate_tvi function.
        player_id_col (str, optional): Name of the column for player IDs. Defaults to 'player_id'.
        playtime_col (str, optional): Name of the column for playtime. Defaults to 'play_time'.
        position_col (str, optional): Name of the column for player positions. Defaults to 'position'.

    Returns:
        pd.DataFrame: Aggregated DataFrame with one row per player.
    """
    tvi_final = tvi_df.copy()

    # Weighted average of metrics
    tvi_final = tvi_final.drop(columns=['team_id', 'game_id', position_col])\
        .groupby([player_id_col]).apply(helpers.weighted_avg, weight_column=playtime_col).reset_index()
    
    # Most played position
    position_time = tvi_df.groupby([player_id_col, position_col])[playtime_col].sum().reset_index()
    most_played_position = position_time.loc[
        position_time.groupby(player_id_col)[playtime_col].idxmax()
    ][[player_id_col, position_col]].rename(columns={position_col: 'main_position'})

    # Total playtime
    total_play_time = tvi_df.groupby([player_id_col])[playtime_col].sum().reset_index()
    total_play_time = total_play_time.rename(columns={playtime_col: 'total_play_time'})

    # Merge data
    tvi_final = pd.merge(tvi_final, most_played_position, on=[player_id_col], how='left')
    tvi_final = pd.merge(tvi_final, total_play_time, on=[player_id_col], how='left')

    # Final adjustments
    tvi_final[playtime_col] = tvi_final['total_play_time']
    tvi_final = tvi_final.drop(columns=['total_play_time'])
    tvi_final = tvi_final.rename(columns={'main_position': position_col})

    return tvi_final.sort_values('TVI', ascending=False)
