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

# NOC modules
from noc.core.service.loader import get_service
from noc.core.hash import hash_int
from noc.core.clickhouse.connect import connection as ch_connection

SQL_STATE = """
    SELECT node_id, argMax(state, ts) as state
    FROM metricstate
    WHERE slot = %s
    GROUP BY node_id
    FORMAT JSONEachRow

"""


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
        state = {}
        ch = ch_connection()
        async with self.lock:
            self.logger.info("Lock acquired")
            n = 0
            result = ch.execute(SQL_STATE % self.slot, return_raw=True)
            for row in result.splitlines():
                row = orjson.loads(row)
                state[row["node_id"]] = orjson.loads(row["state"])
                n += 1
        self.logger.info("%d states are retrieved from %d log items", len(state), n)
        return state

    async def flush(self) -> None:
        """
        Store all collected changes
        """
        states_count = 0
        ts = datetime.datetime.now().replace(microsecond=0)
        async with self.lock:
            if not self.state:
                return  # Nothing to flush
            for (node_id, node_type), state in self.state.items():
                self.service.register_metrics(
                    "metricstate",
                    [
                        {
                            "date": ts.date().isoformat(),
                            "ts": ts.isoformat(),
                            "node_id": node_id,
                            "node_type": node_type,
                            "slot": self.slot,
                            "state": orjson.dumps(state).decode("utf-8"),
                        }
                    ],
                    key=hash_int(node_id),
                )
                states_count += 1
            self.state = {}  # Reset
        self.logger.debug("Flush State Record: %d", states_count)

    async def feed(self, state: Dict[str, Dict[str, Any]]) -> None:
        """
        Feed change to log
        """
        if not state:
            return
        async with self.lock:
            self.state.update(state)
