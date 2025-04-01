# ----------------------------------------------------------------------
# DedupFilter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.fm.event import Event
from noc.core.hash import hash_int, dict_hash_int
from .base import BaseEvFilter
from ..eventconfig import EventConfig


class DedupFilter(BaseEvFilter):
    """
    Event deduplication filter. Filters out event basing on full vars match.
    """

    @staticmethod
    def event_hash(event: Event, event_config: EventConfig, e_vars) -> int:
        var_hash = dict_hash_int(e_vars) if e_vars else 0
        return hash_int(f"{event.target.id}:{event_config.id}:{var_hash}")

    @staticmethod
    def get_window(event_config: EventConfig) -> int:
        if "dedup" not in event_config.filters:
            return 0
        return event_config.filters["dedup"].window
