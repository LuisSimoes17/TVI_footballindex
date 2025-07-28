from math import sqrt
import numpy as np


def assign_zones(x, y, x_min_max=(0, 100), y_min_max=(0, 100), grid_shape=(3, 3), zone_map=[2, 1, 2, 4, 3, 4, 6, 5, 6]):
    """
    Assigns a tactical zone to a given (x, y) coordinate on the football pitch.

    The pitch is divided into a grid, and this function determines which zone the coordinate falls into.
    The grid shape can be customized (e.g., 3x3, 4x3).

    Args:
        x (float): The x-coordinate of the event, typically ranging from 0 to 100.
        y (float): The y-coordinate of the event, typically ranging from 0 to 100.
        x_min_max (tuple, optional): The minimum and maximum values for the x-coordinate. Defaults to (0, 100).
        y_min_max (tuple, optional): The minimum and maximum values for the y-coordinate. Defaults to (0, 100).
        grid_shape (tuple, optional): The shape of the grid as (rows, columns). Defaults to (3, 3).
        zone_map (list, optional): A list that maps the grid index to a specific zone number. The length of the list
                                   must be equal to rows * columns.

    Returns:
        int: The zone number corresponding to the given (x, y) coordinate.

    Raises:
        ValueError: If the length of the zone_map does not match the grid size (rows * columns).
    """
    rows, cols = grid_shape
    if len(zone_map) != rows * cols:
        raise ValueError(
            "The number of zones (rows * cols) should match the length of the zone_map list.")

    x_step = (x_min_max[1] - x_min_max[0]) / cols
    y_step = (y_min_max[1] - y_min_max[0]) / rows
    
    col_index = int(min((x - x_min_max[0]) / x_step, cols - 1))
    row_index = int(min((y - y_min_max[0]) / y_step, rows - 1))
    
    index = row_index * cols + col_index
    return zone_map[index]


def pass_length(start_x, start_y, end_x, end_y,
                pitch_length_coord=100, pitch_width_coord=100,
                pitch_length_meters=105, pitch_width_meters=68):
    """
    Calculates the progression of a pass towards the opponent's goal and the final proximity to the goal.

    This function converts coordinate-based pass locations to meters, then calculates the change in distance
    to the goal line. It also determines whether the pass started and ended in the defensive or attacking half.

    Args:
        start_x (float): The starting x-coordinate of the pass.
        start_y (float): The starting y-coordinate of the pass.
        end_x (float): The ending x-coordinate of the pass.
        end_y (float): The ending y-coordinate of the pass.
        pitch_length_coord (int, optional): The length of the pitch in the coordinate system. Defaults to 100.
        pitch_width_coord (int, optional): The width of the pitch in the coordinate system. Defaults to 100.
        pitch_length_meters (int, optional): The actual length of the pitch in meters. Defaults to 105.
        pitch_width_meters (int, optional): The actual width of the pitch in meters. Defaults to 68.

    Returns:
        tuple: A tuple containing:
            - progression (float): The distance (in meters) the pass moved closer to the opponent's goal.
                                   A positive value indicates progression, negative indicates regression.
            - end_dist (float): The final distance (in meters) from the opponent's goal line.
            - start_half (str): The half of the pitch where the pass started ('defensive half' or 'attacking half').
            - end_half (str): The half of the pitch where the pass ended ('defensive half' or 'attacking half').
    """
    scale_x = pitch_length_meters / pitch_length_coord
    scale_y = pitch_width_meters / pitch_width_coord
    start_x_m = start_x * scale_x
    start_y_m = start_y * scale_y
    end_x_m = end_x * scale_x
    end_y_m = end_y * scale_y
    goal_x = pitch_length_meters
    goal_y = pitch_width_meters / 2
    start_dist = np.sqrt((goal_x - start_x_m)**2 + (goal_y - start_y_m)**2)
    end_dist = np.sqrt((goal_x - end_x_m)**2 + (goal_y - end_y_m)**2)
    progression = start_dist - end_dist
    half_boundary = pitch_length_meters / 2
    start_half = "defensive half" if start_x_m < half_boundary else "attacking half"
    end_half = "defensive half" if end_x_m < half_boundary else "attacking half"
    return progression, end_dist, start_half, end_half


def weighted_avg(df, weight_column):
    """
    Computes the weighted average of all numeric columns in a DataFrame, intended for use with pandas groupby().apply().

    This function is useful for aggregating player statistics where each match or event should be weighted by a
    specific factor, such as minutes played.

    Args:
        df (pd.DataFrame): The DataFrame or sub-DataFrame (from a groupby) on which to perform the weighted average.
        weight_column (str): The name of the column that contains the weights (e.g., 'play_time').

    Returns:
        pd.Series: A Series containing the weighted average for each numeric column, or None if the total weight is zero.
    """
    weights = df[weight_column]
    numeric_cols = df.select_dtypes(include=np.number).columns.drop(weight_column)
    weighted_sum = df[numeric_cols].mul(weights, axis=0).sum()
    total_weight = weights.sum()
    if total_weight == 0:
        return None
    return weighted_sum / total_weight
