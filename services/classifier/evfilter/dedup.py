# ----------------------------------------------------------------------
# DedupFilter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.fm.models.activeevent import ActiveEvent
from noc.core.hash import hash_int, dict_hash_int
from .base import BaseEvFilter


class DedupFilter(BaseEvFilter):
    """
    Event deduplication filter. Filters out event basing on full vars match.
    """

    @staticmethod
    def event_hash(event: ActiveEvent) -> int:
        var_hash = dict_hash_int(event.vars) if event.vars else 0
        return hash_int(f"{event.managed_object.id}:{event.event_class.id}:{var_hash}")

    @staticmethod
    def get_window(event: ActiveEvent) -> int:
        return event.event_class.deduplication_window or 0
