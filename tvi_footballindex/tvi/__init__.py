"""
TVI (Tactical Versatility Index) submodule for football tactical analysis.

Contains functions for calculating the Tactical Versatility Index,
which measures a player's or team's tactical adaptability and flexibility.
"""

from .calculator import (
    calculate_tvi,
    aggregate_tvi_by_player,
)

__all__ = [
    'calculate_tvi',
    'aggregate_tvi_by_player',
]
