from math import sqrt

def assign_zones(x, y, x_min_max=(0, 100), y_min_max=(0, 100), zones = 9, zone_map = [2,1,2,4,3,4,6,5,6]):
    """
    Assigns a zone based on x, y coordinates.

    Parameters:
    x (float): X-coordinate on the pitch.
    y (float): Y-coordinate on the pitch.
    x_min_max (tuple): Min and max range for x-coordinates.
    y_min_max (tuple): Min and max range for y-coordinates.
    zones (int): Number of zones.
    zone_map (list): List of zones identifiers (needs to match the number of zones).

    Returns:
    str: Zone name corresponding to the input coordinates.
    """

    x_y_divisor = sqrt(zones)

    if x_y_divisor != int(x_y_divisor):
        raise ValueError("The number of zones should be a perfect square.")

    if len(zone_map) != zones:
        raise ValueError("The number of zones should match the length of the zone_map list.")

    # split field into 9
    x_step = (x_min_max[1] - x_min_max[0]) / x_y_divisor
    y_step = (y_min_max[1] - y_min_max[0]) / x_y_divisor

    # Determine grid position
    row = int(min((x - x_min_max[0]) / x_step, x_y_divisor-1))  # Ensures max index is 2
    col = int(min((y - y_min_max[0]) / y_step, x_y_divisor-1))

    # Convert row-major indexing to list index
    index = row * 3 + col

    return zone_map[index]
