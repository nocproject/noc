#!./bin/python
# ----------------------------------------------------------------------
# State Change Log
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict
import orjson
import logging
import asyncio
import datetime

# Third-party modules
from pymongo import ASCENDING

# NOC modules
from noc.core.service.loader import get_service


class ChangeLog(object):
    LOCK_CATEGORY = "metrics"
    COLL_NAME = "metricslog"
    MAX_DATA = 15_000_000

    def __init__(self, slot: int):
        self.slot = slot
        self.state: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        self.lock = asyncio.Lock()
        self.service = get_service()

    async def get_state(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve current state snapshot
        """
        self.logger.info("Retrieving current state")
        coll = self.get_collection()
        state = {}
        async with self.lock:
            self.logger.info("Lock acquired")
            n = 0
            async for doc in coll.find({"slot": self.slot}).sort([("_id", ASCENDING)]):
                d = doc.get("data")
                if not d:
                    continue
                state.update(self.decode(doc["data"]))
                n += 1
        self.logger.info("%d states are retrieved from %d log items", len(state), n)
        return state

    async def flush(self) -> None:
        """
        Store all collected changes
        """
        data = []
        ts = datetime.datetime.now().replace(microsecond=0)
        async with self.lock:
            if not self.state:
                return  # Nothing to flush
            for node_id, state in self.state.items():
                data += [
                    {
                        "date": ts.date().isoformat(),
                        "ts": ts.isoformat(),
                        "node_id": node_id,
                        "node_type": "",
                        "slot": self.slot,
                        "state": orjson.dumps(state).decode("utf-8"),
                    }
                ]
            self.state = {}  # Reset
        self.logger.debug("Flush State Record: %d", len(data))
        self.service.register_metrics("metricslog", data)

    async def feed(self, state: Dict[str, Dict[str, Any]]) -> None:
        """
        Feed change to log
        """
        if not state:
            return
        async with self.lock:
            self.state.update(state)
