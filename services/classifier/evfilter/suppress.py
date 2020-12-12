# ----------------------------------------------------------------------
# SuppressFilter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.fm.models.activeevent import ActiveEvent
from noc.core.hash import hash_int, dict_hash_int
from .base import BaseEvFilter


class SuppressFilter(BaseEvFilter):
    """
    Event suppression filter. Filters out event basing on event suppress
    """

    update_deadline = True

    @staticmethod
    def event_hash(event: ActiveEvent) -> int:
        e_vars = {
            v.name: event.vars.get(v.name, "") or ""
            for v in event.event_class.vars
            if v.match_suppress
        }
        var_hash = dict_hash_int(event.vars) if e_vars else 0
        return hash_int(f"{event.managed_object.id}:{event.event_class.id}:{var_hash}")

    @staticmethod
    def get_window(event: ActiveEvent) -> int:
        return event.event_class.suppression_window or 0
