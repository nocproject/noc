# ----------------------------------------------------------------------
# EvFilter
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

NS = 1_000_000_000


class BaseEvFilter(object):
    """
    BaseEvFilter implements in-memory event filtering basing on hashes.

    `event_hash` method must be implemented in subclasses.
    `get_window` method must be implemented in subclasses.
    `register` method assigns event to a filter.
    `find` method returns matched event_id or None
    """

    update_deadline: bool = False

    def __init__(self):
        self.events: Dict[int, Tuple[int, ObjectId]] = {}
        self.pq: List[Tuple[int, int]] = []

    @staticmethod
    def event_hash(event: ActiveEvent) -> int:
        """
        Collapse event to a hash
        :param event:
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def get_window(event: ActiveEvent) -> int:
        """
        Return filter window in seconds or 0, if disabled
        :param event:
        :return:
        """
        raise NotImplementedError

    def register(self, event: ActiveEvent) -> None:
        """
        Register event to filter
        :param event:
        :return:
        """
        fw = self.get_window(event)
        if not fw:
            return  # No deduplication for event class
        now = perf_counter_ns()
        eh = self.event_hash(event)
        r = self.events.get(eh)
        if r and r[0] > now and not self.update_deadline:
            return  # deadline is not expired still
        deadline = now + fw * NS
        heappush(self.pq, (deadline, eh))
        if r and self.update_deadline:
            event_id = r[1]  # Preserve original event id
        else:
            event_id = event.id
        self.events[eh] = (deadline, event_id)

    def find(self, event: ActiveEvent) -> Optional[ObjectId]:
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
