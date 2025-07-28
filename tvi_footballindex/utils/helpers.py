from math import sqrt
import numpy as np


def assign_zones(x, y, x_min_max=(0, 100), y_min_max=(0, 100), zones=9, zone_map=[2, 1, 2, 4, 3, 4, 6, 5, 6]):
    """
    Assigns a zone based on x, y coordinates.
    """
    x_y_divisor = sqrt(zones)
    if x_y_divisor != int(x_y_divisor):
        raise ValueError("The number of zones should be a perfect square.")
    if len(zone_map) != zones:
        raise ValueError(
            "The number of zones should match the length of the zone_map list.")

    x_step = (x_min_max[1] - x_min_max[0]) / x_y_divisor
    y_step = (y_min_max[1] - y_min_max[0]) / x_y_divisor
    row = int(min((x - x_min_max[0]) / x_step, x_y_divisor - 1))
    col = int(min((y - y_min_max[0]) / y_step, x_y_divisor - 1))
    index = row * 3 + col
    return zone_map[index]


def pass_length(start_x, start_y, end_x, end_y,
                pitch_length_coord=100, pitch_width_coord=100,
                pitch_length_meters=105, pitch_width_meters=68):
    """
    Calculates pass progression and final proximity to the opponent's goal.
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
    Computes the weighted average of all numeric columns in a DataFrame for a groupby operation.
    """
    weights = df[weight_column]
    weighted_sum = df.drop(columns=[weight_column]).mul(weights, axis=0).sum()
    total_weight = weights.sum()
    return weighted_sum / total_weight if total_weight != 0 else None