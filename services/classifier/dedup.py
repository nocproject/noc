# ----------------------------------------------------------------------
# DedupFilter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from time import perf_counter_ns
from heapq import heappush, heappop
from typing import Optional, Tuple, List, Dict

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.fm.models.activeevent import ActiveEvent
from noc.core.hash import hash_int, dict_hash_int

NS = 1_000_000_000


class DedupFilter(object):
    def __init__(self):
        self.events: Dict[int, Tuple[int, ObjectId]] = {}
        self.pq: List[Tuple[int, int]] = []

    @staticmethod
    def event_hash(event: ActiveEvent) -> int:
        var_hash = dict_hash_int(event.vars) if event.vars else 0
        return hash_int(f"{event.managed_object.id}:{event.event_class.id}:{var_hash}")

    def register(self, event: ActiveEvent) -> None:
        """
        Register event to dedup filter
        :param event:
        :return:
        """
        dw = event.event_class.deduplication_window
        if not dw:
            return  # No deduplication for event class
        now = perf_counter_ns()
        eh = self.event_hash(event)
        r = self.events.get(eh)
        if r and r[0] > now:
            return  # deadline is not expired still
        deadline = now + dw * NS
        heappush(self.pq, (deadline, eh))
        self.events[eh] = (deadline, event.id)

    def find_duplicated(self, event: ActiveEvent) -> Optional[ObjectId]:
        """
        Check if event is duplicated
        :param event:
        :return: Duplicated event id
        """
        eh = self.event_hash(event)
        r = self.events.get(eh)
        now = perf_counter_ns()
        if r and r[0] > now:
            return r[1]
        # Expire
        while self.pq and self.pq[0][0] < now:
            deadline, eh = heappop(self.pq)
            r = self.events.get(eh)
            if deadline == r[0]:
                del self.events[eh]
        #
        return None
