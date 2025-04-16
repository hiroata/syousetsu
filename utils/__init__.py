#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility functions for the novel generator application.
This module serves as the entry point for the utils package.
"""

from .text_utils import (
    tags_string_to_list,
    tags_list_to_string,
    parse_synopsis
)

from .ai_utils import (
    call_api_for_novel,
    get_episode_summary
)

# Add legacy function aliases for backward compatibility
from .text_utils import generate_random_character_legacy

# Character and location generation
from .character_utils import generate_random_character
from .location_utils import generate_random_location

__all__ = [
    'tags_string_to_list',
    'tags_list_to_string',
    'parse_synopsis',
    'call_api_for_novel',
    'get_episode_summary',
    'generate_random_character',
    'generate_random_location',
    'generate_random_character_legacy'
]