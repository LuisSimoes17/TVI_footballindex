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
    TYPES_DICT,
    QUALIFIERS_DICT
)

# Import from TVI module (when ready)
# from .tvi.calculator import (
#     calculate_tvi,
#     calculate_player_tvi,
#     calculate_team_tvi,
#     get_tvi_components,
#     # ... other TVI functions
# )

from .version import __version__

# Define what gets imported with "from tvi_footballindex import *"
__all__ = [
    # Parsing functions
    'parsef24_folder',
    'explode_event',
    'get_event_types',
    'get_qualifiers',
    'filter_events_by_type',
    'get_game_summary',
    'TYPES_DICT',
    'QUALIFIERS_DICT',
    # TVI functions (add when ready)
    # 'calculate_tvi',
    # 'calculate_player_tvi',
    # 'calculate_team_tvi',
    # 'get_tvi_components',
    # Version
    '__version__'
]