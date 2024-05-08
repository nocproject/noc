# ----------------------------------------------------------------------
# SuppressFilter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.models.event import Event
from noc.core.hash import hash_int, dict_hash_int
from .base import BaseEvFilter


class SuppressFilter(BaseEvFilter):
    """
    Event suppression filter. Filters out event basing on event suppress
    """

    update_deadline = True

    @staticmethod
    def event_hash(event: Event, event_class) -> int:
        # e_vars = {
        #     v.name: event.vars.get(v.name, "") or ""
        #     for v in event_class.vars
        #     if v.match_suppress
        # }
        var_hash = hash_int(sorted(f"{d.name}:{d.value}" for d in event.data)) if True else 0
        return hash_int(f"{event.target.id}:{event_class.id}:{var_hash}")

    @staticmethod
    def get_window(event_class) -> int:
        return event_class.suppression_window or 0
