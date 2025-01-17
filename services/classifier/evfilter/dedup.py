# ----------------------------------------------------------------------
# DedupFilter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.fm.event import Event
from noc.core.hash import hash_int, dict_hash_int
from .base import BaseEvFilter


class DedupFilter(BaseEvFilter):
    """
    Event deduplication filter. Filters out event basing on full vars match.
    """

    @staticmethod
    def event_hash(event: Event, event_class, e_vars) -> int:
        var_hash = dict_hash_int(e_vars) if e_vars else 0
        return hash_int(f"{event.target.id}:{event_class.id if event_class else ''}:{var_hash}")

    @staticmethod
    def get_window(event_class) -> int:
        if not event_class:
            return 5
        return event_class.deduplication_window or 0
