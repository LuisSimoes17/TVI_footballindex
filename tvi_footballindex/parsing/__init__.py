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
    'TYPES_DICT',
    'QUALIFIERS_DICT'
]