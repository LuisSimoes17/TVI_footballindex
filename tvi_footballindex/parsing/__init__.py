"""
Parsing submodule for football data files.

Contains utilities for parsing various football data formats,
starting with F24 XML files.
"""

from .f24_parser import (
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
    get_dribbles,
    get_shots_on_target,
    get_key_passes,
    get_deep_completions,
    get_progressive_passes,
    TYPES_DICT,
    QUALIFIERS_DICT
)

__all__ = [
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
    'get_dribbles',
    'get_shots_on_target',
    'get_key_passes',
    'get_deep_completions',
    'get_progressive_passes',
    'TYPES_DICT',
    'QUALIFIERS_DICT'
]
