# ----------------------------------------------------------------------
# DedupFilter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.models.event import Event
from noc.core.hash import hash_int, dict_hash_int
from .base import BaseEvFilter


class DedupFilter(BaseEvFilter):
    """
    Event deduplication filter. Filters out event basing on full vars match.
    """

    @staticmethod
    def event_hash(event: Event, event_class) -> int:
        var_hash = hash_int(sorted(f"{d.name}:{d.value}" for d in event.data)) if event.data else 0
        return hash_int(f"{event.target.id}:{event_class.id}:{var_hash}")

    @staticmethod
    def get_window(event_class) -> int:
        return event_class.deduplication_window or 0
