"""
TVI Football Index - A Python library for calculating Tactical Versatility Index in football.

This library provides tools for:
- Parsing F24 XML football data files
- Calculating Tactical Versatility Index (TVI) for players and teams
- Processing and analyzing football event data for tactical insights
"""

# Import from submodules
from .parsing.f24_parser import (
    parsef24_folder,
    explode_event,
    get_event_types,
    get_qualifiers,
    filter_events_by_type,
    get_game_summary,
    calculate_player_playtime,
    get_interceptions,
    get_tackles,
    get_aerials,
    TYPES_DICT,
    QUALIFIERS_DICT
)

from .tvi.calculator import (
    calculate_tvi,
    aggregate_tvi_by_player
)

from .utils.helpers import (
    assign_zones
)

__version__ = "0.2.0"

# Define what gets imported with "from tvi_footballindex import *"
__all__ = [
    # Parsing functions
    'parsef24_folder',
    'explode_event',
    'get_event_types',
    'get_qualifiers',
    'filter_events_by_type',
    'get_game_summary',
    'calculate_player_playtime',
    'get_interceptions',
    'get_tackles',
    'get_aerials',
    'TYPES_DICT',
    'QUALIFIERS_DICT',
    # TVI functions
    'calculate_tvi',
    'aggregate_tvi_by_player',
    # Utility functions
    'assign_zones',
    # Version
    '__version__'
]
