# ----------------------------------------------------------------------
# EvFilter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time
from heapq import heappush, heappop
from typing import Optional, Tuple, List, Dict, Any

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.config import config
from noc.core.fm.event import Event
from noc.fm.models.eventclass import EventClass


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
    def event_hash(event: Event, event_class: EventClass, event_vars: Dict[str, Any]) -> int:
        """
        Collapse event to a hash
        Args:
            event: Event instance
            event_class: EventClass Instance
            event_vars: Variables dict
        """
        raise NotImplementedError

    @staticmethod
    def get_window(event_class: EventClass) -> int:
        """
        Return filter window in seconds or 0, if disabled
        :param event_class:
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def _get_timestamp(event: Event) -> int:
        return int(event.timestamp.timestamp())

    def register(
        self, event: Event, event_class: EventClass, event_vars: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register event to filter"""
        fw = self.get_window(event_class)
        if not fw:
            return  # No deduplication for event class
        now = self._get_timestamp(event)
        eh = self.event_hash(event, event_class, event_vars)
        r = self.events.get(eh)
        if r and r[0] > now and not self.update_deadline:
            return  # deadline is not expired still
        deadline = now + fw
        heappush(self.pq, (deadline, eh))
        if r and self.update_deadline:
            event_id = r[1]  # Preserve original event id
        else:
            event_id = event.id
        self.events[eh] = (deadline, event_id)

    def find(
        self, event: Event, event_class: EventClass, event_vars: Optional[Dict[str, Any]] = None
    ) -> Optional[ObjectId]:
        """Check if event is duplicated"""
        eh = self.event_hash(event, event_class, event_vars)
        r = self.events.get(eh)
        ts = self._get_timestamp(event)
        if r and r[0] > ts:
            return r[1]
        # Expire
        threshold = int(time.time()) - config.classifier.allowed_time_drift
        while self.pq and self.pq[0][0] < threshold:
            deadline, eh = heappop(self.pq)
            r = self.events.get(eh)
            if deadline == r[0]:
                del self.events[eh]
        #
        return None
