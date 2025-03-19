# ----------------------------------------------------------------------
# FM Event Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC Modules
import datetime

# Third-party module
import orjson

# NOC modules
from .base import BaseLoader
from ..models.fmevent import FMEventObject
from noc.core.fm.event import Event, EventSeverity, MessageType, Var
from noc.core.service.loader import get_service
from noc.core.bi.decorator import bi_hash


class FMEventLoader(BaseLoader):
    """
    FM Event loader
    """

    name = "fmevent"
    data_model = FMEventObject

    def get_fm_event(self, e: FMEventObject) -> Event:
        """
        Register FM Event for send to classifier

        Args:
            e: timestamp
        """
        if not e.data and not e.message:
            raise AttributeError("Unknown message data. Set data or message")
        severity = EventSeverity(int(e.severity)) if e.severity else EventSeverity.INDETERMINATE
        event = Event(
            ts=e.ts,
            remote_id=e.id,
            remote_system=self.system.remote_system.name,
            target=e.object.get_target(),
            type=MessageType(
                severity=severity if not e.is_cleared else EventSeverity.CLEARED,
                event_class=e.event_class,
                categories=e.categories or None,
            ),
            data=[Var(name=d.name, value=d.value) for d in e.data],
            message=e.message,
            labels=e.labels,
        )
        event.target.pool = e.object.pool or "default"
        return event

    def load(self):
        """
        Import new data
        """
        self.logger.info("Importing")
        ns = self.get_new_state()
        if not ns:
            self.logger.info("No new state, skipping")
            self.load_mappings()
            return
        new_state = self.iter_jsonl(ns)

        svc = get_service()
        max_ts, num = 0, 0
        for num, event in enumerate(new_state):
            event = self.get_fm_event(event)
            max_ts = max(max_ts, event.ts)
            svc.publish(orjson.dumps(event.model_dump()), f"events.{event.target.pool}")
        if max_ts:
            self.system.remote_system.last_extract_event = datetime.datetime.fromtimestamp(max_ts)
            return
        now = datetime.datetime.now().replace(microsecond=0)
        if not self.system.remote_system.last_extract_event:
            self.system.remote_system.last_extract_event = now
        else:
            le = self.system.remote_system.last_extract_event + datetime.timedelta(days=1)
            self.system.remote_system.last_extract_event = min(le, now)
        self.logger.info("Last extract event TS: %s", self.system.remote_system.last_extract_event)
        self.logger.info("Send FM Event: %s", num)

    def check(self, chain):
        return 0
