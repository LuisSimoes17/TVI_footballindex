"""
F24 XML Parser

This module contains utility functions for parsing F24 XML football data files
and processing football event data for analysis and metric calculations.

Part of the tvi_footballindex library.
"""

import xml.etree.ElementTree as et
import pandas as pd
from pandas import json_normalize
import pandas as pd
import os
from tqdm import tqdm

# Configure pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 20)

# Event types dictionary mapping type IDs to event names
TYPES_DICT = {
    1: "Pass", 2: "Offside Pass", 3: "Take On", 4: "Foul", 5: "Out", 
    6: "Corner Awarded", 7: "Tackle", 8: "Interception", 9: "Turnover", 
    10: "Save", 11: "Claim", 12: "Clearance", 13: "Miss", 14: "Post", 
    15: "Attempt Saved", 16: "Goal", 17: "Card", 18: "Player off", 
    19: "Player on", 20: "Player retired", 21: "Player returns", 
    22: "Player becomes goalkeeper", 23: "Goalkeeper becomes player", 
    24: "Condition change", 25: "Official change", 27: "Start delay", 
    28: "End delay", 30: "End", 31: "Picked an orange", 32: "Start", 
    34: "Team set up", 35: "Player changed position", 
    36: "Player changed Jersey number", 37: "Collection End", 
    38: "Temp_Goal", 39: "Temp_Attempt", 40: "Formation change", 
    41: "Punch", 42: "Good Skill", 43: "Deleted event", 44: "Aerial", 
    45: "Challenge", 47: "Rescinded card", 49: "Ball recovery", 
    50: "Dispossessed", 51: "Error", 52: "Keeper pick-up", 
    53: "Cross not claimed", 54: "Smother", 55: "Offside provoked", 
    56: "Shield ball opp", 57: "Foul throw-in", 58: "Penalty faced", 
    59: "Keeper Sweeper", 60: "Chance missed", 61: "Ball touch", 
    63: "Temp_Save", 64: "Resume", 65: "Contentious referee decision", 
    67: "50/50", 68: "Referee drop ball", 69: "Failed To Block", 
    72: "Caught offside", 73: "Other Ball Contact", 74: "Blocked pass"
}

# Qualifiers dictionary mapping qualifier IDs to descriptions
QUALIFIERS_DICT = {
    1: "Long ball", 2: "Cross", 3: "Head pass", 4: "Through ball", 
    5: "Free kick taken", 6: "Corner taken", 7: "Players caught offside", 
    8: "Goal disallowed", 9: "Penalty", 10: "Hand", 11: "6-seconds violation", 
    12: "Dangerous play", 13: "Foul", 14: "Last line", 15: "Head", 
    16: "Small box-centre", 17: "Box-centre", 18: "Out of box-centre", 
    19: "35+ centre", 20: "Right footed", 21: "Other body part", 
    22: "Regular play", 23: "Fast break", 24: "Set piece", 25: "From corner", 
    26: "Free kick", 28: "Own goal", 29: "Assisted", 30: "Involved", 
    31: "Yellow Card", 32: "Second yellow", 33: "Red card", 34: "Referee abuse", 
    35: "Argument", 36: "Fight", 37: "Time wasting", 38: "Excessive celebration", 
    39: "Crowd interaction", 40: "Other reason", 41: "Injury", 42: "Tactical", 
    44: "Player position", 49: "Attendance figure", 50: "Official position", 
    51: "Official ID", 53: "Injured player id", 54: "End cause", 
    55: "Related event ID", 56: "Zone", 57: "End type", 59: "Jersey number", 
    60: "Small box-right", 61: "Small box-left", 62: "Box-deep right", 
    63: "Box-right", 64: "Box-left", 65: "Box-deep left", 66: "Out of box-deep right", 
    67: "Out of box-right", 68: "Out of box-left", 69: "Out of box-deep left", 
    70: "35+ right", 71: "35+ left", 72: "Left footed", 73: "Left", 74: "High", 
    75: "Right", 76: "Low left", 77: "High left", 78: "Low centre", 
    79: "High centre", 80: "Low right", 81: "High right", 82: "Blocked", 
    83: "Close left", 84: "Close right", 85: "Close high", 86: "Close left and high", 
    87: "Close right and high", 88: "High claim", 89: "1 on 1", 90: "Deflected save", 
    91: "Dive and deflect", 92: "Catch", 93: "Dive and catch", 94: "Def block", 
    95: "Back pass", 96: "Corner situation", 97: "Direct free", 100: "Six yard blocked", 
    101: "Saved off line", 102: "Goal mouth y co-ordinate", 103: "Goal mouth z co-ordinate", 
    106: "Attacking Pass", 107: "Throw-in", 108: "Volley", 109: "Overhead", 
    110: "Half Volley", 111: "Diving Header", 112: "Scramble", 113: "Strong", 
    114: "Weak", 115: "Rising", 116: "Dipping", 117: "Lob", 118: "One Bounce", 
    119: "Few Bounces", 120: "Swerve Left", 121: "Swerve Right", 122: "Swerve Moving", 
    123: "Keeper Throw", 124: "Goal Kick", 127: "Direction of play", 128: "Punch", 
    130: "Team formation", 131: "Team player formation", 132: "Dive", 133: "Deflection", 
    134: "Far Wide Left", 135: "Far Wide Right", 136: "Keeper Touched", 
    137: "Keeper Saved", 138: "Hit Woodwork", 139: "Own Player", 140: "Pass End X", 
    141: "Pass End Y", 144: "Deleted event type", 145: "Formation slot", 
    146: "Blocked x co-ordinate", 147: "Blocked y co-ordinate", 153: "Not past goal line", 
    154: "Intentional assist", 155: "Chipped", 156: "Lay-off", 157: "Launch", 
    158: "Persistent infringement", 159: "Foul and abusive language", 
    160: "Throw-in set piece", 161: "Encroachment", 162: "Leaving field", 
    163: "Entering field", 164: "Spitting", 165: "Professional foul", 
    166: "Handling on the line", 167: "Out of play", 168: "Flick-on", 
    169: "Leading to attempt", 170: "Leading to goal", 171: "Rescinded card", 
    172: "No impact on timing", 173: "Parried safe", 174: "Parried danger", 
    175: "Fingertip", 176: "Caught", 177: "Collected", 178: "Standing", 
    179: "Diving", 180: "Stooping", 181: "Reaching", 182: "Hands", 183: "Feet", 
    184: "Dissent", 185: "Blocked cross", 186: "Scored", 187: "Saved", 
    188: "Missed", 189: "Player not visible", 190: "From shot off target", 
    191: "Off the ball foul", 192: "Block by hand", 194: "Captain", 195: "Pull Back", 
    196: "Switch of play", 197: "Team kit", 198: "GK hoof", 199: "Gk kick from hands", 
    200: "Referee stop", 201: "Referee delay", 202: "Weather problem", 
    203: "Crowd trouble", 204: "Fire", 205: "Object thrown on pitch", 
    206: "Spectator on pitch", 207: "Awaiting officials decision", 
    208: "Referee Injury", 209: "Game end", 210: "Assist", 211: "Overrun", 
    212: "Length", 213: "Angle", 214: "Big Chance", 215: "Individual Play", 
    216: "2nd related event ID", 217: "2nd assisted", 218: "2nd assist", 
    219: "Players on both posts", 220: "Player on near post", 221: "Player on far post", 
    222: "No players on posts", 223: "In-swinger", 224: "Out-swinger", 
    225: "Straight", 226: "Suspended", 227: "Resume", 228: "Own shot blocked", 
    229: "Post-match complete", 230: "GK X Coordinate", 231: "GK Y Coordinate", 
    232: "Unchallenged"
}

# Create DataFrames for lookups
types = pd.DataFrame.from_dict(TYPES_DICT, orient='index').reset_index()
types.columns = ["type_id", "event_name"]

qualifiers = pd.DataFrame.from_dict(QUALIFIERS_DICT, orient='index').reset_index()
qualifiers.columns = ["qualifier_id", "description"]

# String version of qualifiers dict for column renaming
qualifiers_dict2 = {str(key): str(value) for key, value in QUALIFIERS_DICT.items()}


def parsef24_folder(F24folder, show_progress=True):
    """
    Parse F24 XML files from a folder and return game and event data.
    
    Parameters:
    -----------
    F24folder : str
        Path to the folder containing F24 XML files
    show_progress : bool, default True
        Whether to show progress bar   

    Returns:
    --------
    pandas.DataFrame
        DataFrame containing all match events with game metadata
    """
    games_list = []
    events_list = []

    files = [f for f in os.listdir(F24folder) if f.endswith(".xml")]
    iterator = tqdm(files) if show_progress else files

    for file in iterator:
        if file.endswith(".xml"):
            file_path = os.path.join(F24folder, file)
            
            tree = et.ElementTree(file=file_path)
            games = tree.getroot()
            gameinfo = games.findall('Game')[0]  # Assuming there's always one 'Game' element

            # Cache game metadata
            game_id = gameinfo.get('id')
            game_meta = {
                "game_id": game_id,
                "home_team_id": gameinfo.get('home_team_id'),
                "home_team_name": gameinfo.get('home_team_name'),
                "away_team_id": gameinfo.get('away_team_id'),
                "away_team_name": gameinfo.get('away_team_name'),
                "competition_id": gameinfo.get('competition_id'),
                "competition_name": gameinfo.get('competition_name'),
                "season_id": gameinfo.get('season_id'),
            }
            games_list.append(game_meta)

            for game in games:
                for event in game:
                    # Build a dictionary for the event data
                    event_data = event.attrib.copy()
                    # Use list comprehension to extract qualifiers
                    event_data["qualifiers"] = [q.attrib for q in event]
                    event_data["game_id"] = game_id  # Attach game metadata to event
                    # Build a DataFrame for this event and append it to the list
                    events_list.append(event_data)

    # Concatenate all parsed events into a single DataFrame
    game_df = pd.DataFrame(games_list)
    match_events = pd.DataFrame(events_list)

    # Convert data types
    match_events[["id", "event_id", "type_id", "period_id", "min", "sec"]] = \
        match_events[["id", "event_id", "type_id", "period_id", "min", "sec"]].astype(int)
    match_events[["y", "x"]] = match_events[["y", "x"]].astype(float)
    
    # Merge with event types
    match_events = pd.merge(match_events, types, on="type_id", how="left")
    
    # Reorder columns to put important ones first
    match_events = match_events[['id', "event_id", "type_id", "event_name"] + 
                               [col for col in match_events.columns if col not in 
                                ['id', "event_id", "type_id", "event_name"]]]

    # Add game info to match_events
    match_events = pd.merge(match_events, game_df, on="game_id", how="inner")

    match_events['outcome'] = match_events['outcome'].astype(int)

    return match_events


def explode_event(nome_df, id_evento, mytresh):
    """
    Explode qualifiers for a specific event type and pivot them into columns.
    
    Parameters:
    -----------
    nome_df : pandas.DataFrame
        DataFrame containing match events
    id_evento : int
        Event type ID to filter for
    mytresh : float
        Threshold for minimum non-NA values to keep columns (0-1)
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with exploded qualifiers as columns
    """
    # Filter the dataframe for the required event type
    nome_df = nome_df[nome_df["type_id"] == id_evento].copy()

    if nome_df.empty:
        return pd.DataFrame()  # Return empty if no matching events

    # Explode 'qualifiers' column (assuming it's a list of dictionaries)
    nome_df_exploded = nome_df.explode("qualifiers")

    # Normalize the qualifiers column
    qualifiers_df = pd.json_normalize(nome_df_exploded["qualifiers"]).fillna("yes")

    # Add the event ID back to qualifiers_df
    qualifiers_df["id"] = nome_df_exploded["id"].values

    # Pivot table
    qualifiers_df = qualifiers_df\
        .pivot_table(index='id', columns='qualifier_id', values='value', aggfunc='first')\
        .reset_index()

    # Rename columns based on qualifiers dictionary
    qualifiers_df.rename(columns=qualifiers_dict2, inplace=True)

    # Drop columns that have too many NaN values
    min_non_na = len(qualifiers_df) * mytresh
    qualifiers_df = qualifiers_df.dropna(thresh=min_non_na, axis=1)

    # Drop the original exploded 'qualifiers' column
    nome_df = nome_df.drop(columns=["qualifiers"])

    # Merge back
    exploded_df = nome_df.merge(qualifiers_df, on="id", how="outer").fillna("-")

    return exploded_df


def get_event_types():
    """
    Get DataFrame of event types.
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with type_id and event_name columns
    """
    return types.copy()


def get_qualifiers():
    """
    Get DataFrame of qualifiers.
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with qualifier_id and description columns
    """
    return qualifiers.copy()


def filter_events_by_type(df, event_types):
    """
    Filter events by event type(s).
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing match events
    event_types : int, str, or list
        Event type ID(s) or name(s) to filter for
        
    Returns:
    --------
    pandas.DataFrame
        Filtered DataFrame
    """
    if isinstance(event_types, (int, str)):
        event_types = [event_types]
    
    # Check if we're filtering by ID or name
    if all(isinstance(et, int) for et in event_types):
        return df[df['type_id'].isin(event_types)]
    elif all(isinstance(et, str) for et in event_types):
        return df[df['event_name'].isin(event_types)]
    else:
        raise ValueError("event_types must be all integers (IDs) or all strings (names)")


def get_game_summary(df):
    """
    Get summary statistics for games in the dataset.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing match events
        
    Returns:
    --------
    pandas.DataFrame
        Summary statistics by game
    """
    summary = df.groupby(['game_id', 'home_team_name', 'away_team_name']).agg({
        'id': 'count',
        'type_id': 'nunique',
        'event_name': lambda x: x.value_counts().to_dict()
    }).reset_index()
    
    summary.columns = ['game_id', 'home_team', 'away_team', 'total_events', 'unique_event_types', 'event_breakdown']
    
    return summary


def calculate_player_playtime(match_events, min_playtime=30, clip_to_90=True):
    """
    Calculate playtime for each player in each game.
    
    This function determines how long each player was on the field by tracking
    starting lineups, substitutions in, and substitutions out.
    
    Parameters:
    -----------
    match_events : pandas.DataFrame
        DataFrame containing match events
    min_playtime : int, optional
        Minimum playtime threshold in minutes (default: 30)
        Players with less playtime will be filtered out
        Set to 0 to include all players
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with columns: game_id, team_id, player_id, play_time
        Only includes players meeting the minimum playtime threshold
    """
    # Event type IDs for player tracking
    starting_eleven_id = 34  # Team set up
    player_on_id = 19        # Player on (substitution in)
    player_off_id = 18       # Player off (substitution out)
    
    # Get starting eleven players
    starting_eleven = explode_event(match_events, starting_eleven_id, 0)[['game_id', 'team_id', 'Involved']]
    
    if starting_eleven.empty:
        # If no starting eleven data, return empty DataFrame
        return pd.DataFrame(columns=['game_id', 'team_id', 'player_id', 'play_time'])
    
    # Get only first 11 players involved and clean the data
    starting_eleven['Involved'] = starting_eleven['Involved'].str.split(',').str[:11]\
      .apply(lambda x: [name.strip() for name in x])  # Remove spaces
    
    # Explode 'Involved' column to get one row per player
    starting_eleven = starting_eleven.explode('Involved')
    starting_eleven = starting_eleven.reset_index(drop=True)\
      .rename(columns={'Involved': 'player_id'})
    starting_eleven['start_time'] = 0
    
    # Get substitution events
    sub_ons = match_events[match_events['type_id'] == player_on_id][['game_id', 'team_id', 'player_id', 'min']]\
      .rename(columns={'min': 'start_time'}).reset_index(drop=True)
    
    sub_offs = match_events[match_events['type_id'] == player_off_id][['game_id', 'team_id', 'player_id', 'min']]\
      .rename(columns={'min': 'end_time'}).reset_index(drop=True)
    
    # Combine starting eleven and substitutions
    play_time = pd.concat([starting_eleven, sub_ons], axis=0)
    play_time = pd.merge(play_time, sub_offs, on=['game_id', 'team_id', 'player_id'], how='left')
    
    # Fill missing end times with 90 minutes (full game)
    play_time['end_time'] = play_time['end_time'].fillna(90)
    
    # Calculate actual playtime
    play_time['play_time'] = play_time['end_time'] - play_time['start_time']
    
    # Optionally limit play_time to maximum 90 minutes
    if clip_to_90:
        play_time['play_time'] = play_time['play_time'].clip(upper=90)
    
    # Clean up columns
    play_time = play_time.drop(['start_time', 'end_time'], axis=1)
    
    # Filter by minimum playtime threshold
    if min_playtime > 0:
        play_time = play_time[play_time['play_time'] >= min_playtime]
    
    return play_time.reset_index(drop=True)


def get_interceptions(match_events, successful_only=True, include_coordinates=True):
    """
    Get interception actions for all players.
    
    Parameters:
    -----------
    match_events : pandas.DataFrame
        DataFrame containing match events
    successful_only : bool, optional
        Whether to include only successful interceptions (default: True)
    include_coordinates : bool, optional
        Whether to include x,y coordinates (default: True)
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with interception actions
    """
    interception_id = 8
    
    # Filter for interceptions
    interceptions = match_events[match_events['type_id'] == interception_id]
    
    if interceptions.empty:
        columns = ['game_id', 'team_id', 'player_id', 'event_name']
        if include_coordinates:
            columns.extend(['x', 'y'])
        return pd.DataFrame(columns=columns)
    
    # Filter for successful actions if requested
    if successful_only:
        interceptions = interceptions[interceptions['outcome'] == 1]
    
    # Select relevant columns
    columns = ['game_id', 'team_id', 'player_id', 'event_name']
    if include_coordinates:
        columns.extend(['x', 'y'])
    
    return interceptions[columns].reset_index(drop=True)


def get_tackles(match_events, successful_only=True, include_coordinates=True):
    """
    Get tackle actions for all players.
    
    Parameters:
    -----------
    match_events : pandas.DataFrame
        DataFrame containing match events
    successful_only : bool, optional
        Whether to include only successful tackles (default: True)
    include_coordinates : bool, optional
        Whether to include x,y coordinates (default: True)
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with tackle actions
    """
    tackle_id = 7
    
    # Filter for tackles
    tackles = match_events[match_events['type_id'] == tackle_id]
    
    if tackles.empty:
        columns = ['game_id', 'team_id', 'player_id', 'event_name']
        if include_coordinates:
            columns.extend(['x', 'y'])
        return pd.DataFrame(columns=columns)
    
    # Filter for successful actions if requested
    if successful_only:
        tackles = tackles[tackles['outcome'] == 1]
    
    # Select relevant columns
    columns = ['game_id', 'team_id', 'player_id', 'event_name']
    if include_coordinates:
        columns.extend(['x', 'y'])
    
    return tackles[columns].reset_index(drop=True)


def get_aerials(match_events, successful_only=True, include_coordinates=True):
    """
    Get aerial duel actions for all players.
    
    Parameters:
    -----------
    match_events : pandas.DataFrame
        DataFrame containing match events
    successful_only : bool, optional
        Whether to include only successful aerials (default: True)
    include_coordinates : bool, optional
        Whether to include x,y coordinates (default: True)
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with aerial duel actions
    """
    aerial_id = 44
    
    # Filter for aerials
    aerials = match_events[match_events['type_id'] == aerial_id]
    
    if aerials.empty:
        columns = ['game_id', 'team_id', 'player_id', 'event_name']
        if include_coordinates:
            columns.extend(['x', 'y'])
        return pd.DataFrame(columns=columns)
    
    # Filter for successful actions if requested
    if successful_only:
        aerials = aerials[aerials['outcome'] == 1]
    
    # Select relevant columns
    columns = ['game_id', 'team_id', 'player_id', 'event_name']
    if include_coordinates:
        columns.extend(['x', 'y'])
    
    return aerials[columns].reset_index(drop=True)

def get_dribbles(match_events, successful_only=True, include_coordinates=True):
    """
    Get dribble (take on) actions for all players.

    Parameters
    ----------
    match_events : pandas.DataFrame
        DataFrame containing match events.
    successful_only : bool, optional
        Whether to include only successful dribbles (default: True).
    include_coordinates : bool, optional
        Whether to include x, y coordinates (default: True).

    Returns
    -------
    pandas.DataFrame
        DataFrame with dribble actions, including columns:
            - 'game_id'
            - 'team_id'
            - 'player_id'
            - 'event_name' (set to 'dribble')
            - 'x', 'y' (if include_coordinates is True)
        The DataFrame is indexed from 0.
    """
    dribble_id = 3
    dribbles = match_events[match_events['type_id'] == dribble_id]
    if successful_only:
        dribbles = dribbles[dribbles['outcome'] == 1]
    dribbles = dribbles.copy()
    dribbles['event_name'] = 'dribble'
    columns = ['game_id', 'team_id', 'player_id', 'event_name']
    if include_coordinates:
        columns.extend(['x', 'y'])
    return dribbles[columns].reset_index(drop=True)

def get_shots_on_target(match_events, include_coordinates=True):
    """
    Extracts shots on target from a DataFrame of match events.

    Shots on target are defined as shots that are either saved (not blocked) or result in a goal.

    Parameters
    ----------
    match_events : pd.DataFrame
        DataFrame containing match event data.
    include_coordinates : bool, optional
        If True, includes the shot coordinates ('x', 'y') in the output. Default is True.

    Returns
    -------
    pd.DataFrame
        DataFrame containing shots on target with columns:
            - 'game_id'
            - 'team_id'
            - 'player_id'
            - 'event_name' (set to 'shots_on_target')
            - 'x', 'y' (if include_coordinates is True)
        The DataFrame is indexed from 0.
    """
    shots_saved_id = 15
    goals_id = 16
    shots_saved = match_events[match_events['type_id'] == shots_saved_id]
    goals = match_events[match_events['type_id'] == goals_id]
    shots_saved = explode_event(shots_saved, shots_saved_id, 0)
    shots_saved = shots_saved[shots_saved['Blocked'] != 'yes']
    shots_on_target = pd.concat([
        shots_saved[['game_id', 'team_id', 'player_id', 'x', 'y']],
        goals[['game_id', 'team_id', 'player_id', 'x', 'y']]
    ])
    shots_on_target['event_name'] = 'shots_on_target'
    if not include_coordinates:
        shots_on_target = shots_on_target.drop(columns=['x', 'y'])
    return shots_on_target.reset_index(drop=True)

def get_key_passes(match_events, successful_only=True, include_coordinates=True):
    """
    Extracts key passes from a DataFrame of match events.

    A key pass is defined as a pass that directly leads to a shot attempt.

    Parameters
    ----------
    match_events : pd.DataFrame
        DataFrame containing match event data.
    successful_only : bool, optional
        If True, only considers successful passes. Default is True.
    include_coordinates : bool, optional
        If True, includes the starting coordinates ('x', 'y') of the pass in the output. Default is True.

    Returns
    -------
    pd.DataFrame
        DataFrame containing key passes with columns:
            - 'game_id'
            - 'team_id'
            - 'player_id'
            - 'event_name' (set to 'key_pass')
            - 'x', 'y' (if include_coordinates is True)
        The DataFrame is indexed from 0.
    """
    pass_id = 1
    passes_df = match_events[(match_events['type_id'] == pass_id)]
    if successful_only:
        passes_df = passes_df[passes_df['outcome'] == 1]
    key_passes = passes_df[~passes_df['keypass'].isna()]
    key_passes['event_name'] = 'key_pass'
    columns = ['game_id', 'team_id', 'player_id', 'event_name']
    if include_coordinates:
        columns.extend(['x', 'y'])
    return key_passes[columns].reset_index(drop=True)

def get_deep_completions(
    match_events,
    successful_only=True,
    length_deep_completion=20,
    include_coordinates=True
):
    """
    Extracts deep completions from a DataFrame of match events.

    A deep completion is defined as a completed pass whose ending point is within a certain
    distance (length_deep_completion) from the opponent's goal (i.e., 'end_dist' < threshold).

    Parameters
    ----------
    match_events : pd.DataFrame
        DataFrame containing match event data.
    successful_only : bool, optional
        If True, only considers successful passes. Default is True.
    length_deep_completion : float, optional
        Maximum distance from goal for a pass to be considered a deep completion. Default is 20.
    include_coordinates : bool, optional
        If True, includes the starting coordinates ('x', 'y') of the pass in the output. Default is True.

    Returns
    -------
    pd.DataFrame
        DataFrame containing deep completions with columns:
            - 'game_id'
            - 'team_id'
            - 'player_id'
            - 'event_name' (set to 'deep_completion')
            - 'x', 'y' (if include_coordinates is True)
        The DataFrame is indexed from 0.
    """
    pass_id = 1
    passes_df = match_events[(match_events['type_id'] == pass_id)]
    if successful_only:
        passes_df = passes_df[passes_df['outcome'] == 1]
    passes_exploded = explode_event(passes_df, pass_id, 0.15)
    passes_exploded['pass_end_x'] = passes_exploded['Pass End X'].astype('float')
    passes_exploded['pass_end_y'] = passes_exploded['Pass End Y'].astype('float')
    passes_exploded[['pass_progression', 'end_dist', 'start_half', 'end_half']] = passes_exploded.apply(
        lambda row: pd.Series(pass_length(row['x'], row['y'], row['pass_end_x'], row['pass_end_y'])), axis=1)
    deep_completion = passes_exploded[passes_exploded['end_dist'] < length_deep_completion]
    deep_completion['event_name'] = 'deep_completion'
    columns = ['game_id', 'team_id', 'player_id', 'event_name']
    if include_coordinates:
        columns.extend(['x', 'y'])
    return deep_completion[columns].reset_index(drop=True)

def get_progressive_passes(match_events, successful_only=True, length_threshold=[30, 15, 10], include_coordinates=True):
    def get_progressive_passes(
        match_events,
        successful_only=True,
        length_threshold=[30, 15, 10],
        include_coordinates=True
    ):
        """
        Extracts progressive passes from a DataFrame of match events.

        A progressive pass is defined as a pass that moves the ball significantly closer to the opponent's goal,
        based on the starting and ending halves of the pitch and configurable distance thresholds.

        Args:
            match_events (pd.DataFrame): DataFrame containing event data for a match, including pass events.
            successful_only (bool, optional): If True, only considers successful passes. Defaults to True.
            length_threshold (list of float, optional): Minimum progression distances (in meters or pitch units) for a pass to be considered progressive, depending on the start and end halves:
                - [0]: Defensive half to defensive half
                - [1]: Defensive half to attacking half
                - [2]: Attacking half to attacking half
                Defaults to [30, 15, 10].
            include_coordinates (bool, optional): If True, includes the starting coordinates ('x', 'y') of the pass in the output. Defaults to True.

        Returns:
            pd.DataFrame: DataFrame containing progressive passes with columns:
                - 'game_id'
                - 'team_id'
                - 'player_id'
                - 'event_name' (set to 'progressive_pass')
                - 'x', 'y' (if include_coordinates is True)
            The DataFrame is indexed from 0.

        Notes:
            - Relies on helper functions `explode_event` and `pass_length` to process and calculate pass progression.
            - Assumes the input DataFrame contains columns: 'type_id', 'outcome', 'Pass End X', 'Pass End Y', 'x', 'y', 'game_id', 'team_id', 'player_id'.
            - The function filters passes based on their progression distance and the halves of the pitch they start and end in.
        """
        # function implementation...
    pass_id = 1
    passes_df = match_events[(match_events['type_id'] == pass_id)]
    if successful_only:
        passes_df = passes_df[passes_df['outcome'] == 1]
    passes_exploded = explode_event(passes_df, pass_id, 0.15)
    passes_exploded['pass_end_x'] = passes_exploded['Pass End X'].astype('float')
    passes_exploded['pass_end_y'] = passes_exploded['Pass End Y'].astype('float')
    passes_exploded[['pass_progression', 'end_dist', 'start_half', 'end_half']] = passes_exploded.apply(
        lambda row: pd.Series(pass_length(row['x'], row['y'], row['pass_end_x'], row['pass_end_y'])), axis=1)
    progressive_passes = passes_exploded[
        ((passes_exploded['start_half'] == 'defensive half') & (passes_exploded['end_half'] == 'defensive half') & (passes_exploded['pass_progression'] > length_threshold[0])) |
        ((passes_exploded['start_half'] == 'defensive half') & (passes_exploded['end_half'] == 'attacking half') & (passes_exploded['pass_progression'] > length_threshold[1])) |
        ((passes_exploded['start_half'] == 'attacking half') & (passes_exploded['end_half'] == 'attacking half') & (passes_exploded['pass_progression'] > length_threshold[2]))]
    progressive_passes['event_name'] = 'progressive_pass'
    columns = ['game_id', 'team_id', 'player_id', 'event_name']
    if include_coordinates:
        columns.extend(['x', 'y'])
    return progressive_passes[columns].reset_index(drop=True)