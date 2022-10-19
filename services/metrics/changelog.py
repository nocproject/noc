#!./bin/python
# ----------------------------------------------------------------------
# State Change Log
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict, List, Iterable
import orjson
import logging
import asyncio

# Third-party modules
import lz4.frame
from pymongo import InsertOne, DeleteMany, ASCENDING, DESCENDING
from pymongo.collection import Collection
from bson import ObjectId

# NOC modules
from noc.core.mongo.connection_async import get_db


class ChangeLog(object):
    LOCK_CATEGORY = "metrics"
    COLL_NAME = "metricslog"
    MAX_DATA = 15_000_000

    def __init__(self, slot: int):
        self.slot = slot
        self.state: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        self.lock = asyncio.Lock()

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

    @classmethod
    def get_collection(cls) -> Collection:
        """
        Get mongo collection instance
        """
        return get_db()[cls.COLL_NAME]

    async def flush(self) -> None:
        """
        Store all collected changes
        """
        coll = self.get_collection()
        async with self.lock:
            if not self.state:
                return  # Nothing to flush
            bulk = [
                InsertOne({"_id": ObjectId(), "slot": self.slot, "data": c_data})
                for c_data in self.iter_state_bulks(self.state)
            ]
            self.state = {}  # Reset
        self.logger.debug("Flush State Record: %d", len(bulk))
        await coll.bulk_write(bulk, ordered=True)

    @staticmethod
    def encode(data: Dict[str, Dict[str, Any]]) -> bytes:
        """
        Encode state to bytes
        """
        r = orjson.dumps(data)
        return lz4.frame.compress(r)

    @staticmethod
    def decode(data: bytes) -> Dict[str, Dict[str, Any]]:
        """
        Decode bytes to state
        """
        r = lz4.frame.decompress(data)
        return orjson.loads(r)

    async def feed(self, state: Dict[str, Dict[str, Any]]) -> None:
        """
        Feed change to log
        """
        if not state:
            return
        async with self.lock:
            self.state.update(state)

    @classmethod
    def iter_state_bulks(cls, state: Dict[str, Dict[str, Any]]) -> Iterable[bytes]:
        """
        Compress state to binary chunks up to MAX_DATA size
        """
        c_data = cls.encode(state)
        if len(c_data) < cls.MAX_DATA:
            yield c_data  # Fit
            return
        # Too large, split in halves
        parts: List[Dict[str, Dict[str, Any]]] = [{}, {}]
        lp = len(parts)
        for n, key in enumerate(state):
            parts[n % lp][key] = state[key]
        for p in parts:
            if p:
                yield from cls.iter_state_bulks(p)

    async def compact(self) -> None:
        """
        Compact log
        """
        self.logger.info("Compacting log")
        coll = self.get_collection()
        state = {}
        n = 0
        nn = 0
        prev_size = 0
        next_size = 0
        async with self.lock:
            self.logger.info("Lock acquired")
            # Get maximal id
            max_id = await coll.find_one(
                {"slot": self.slot}, {"_id": 1}, sort=[("_id", DESCENDING)]
            )
            if not max_id:
                self.logger.info("Nothing to compact")
                return
            t_mark = max_id["_id"].generation_time
            t_mark_id = ObjectId.from_datetime(t_mark)
            # Read all states
            async for doc in coll.find(
                {"_id": {"$lte": t_mark_id}, "slot": self.slot}, {"_id": 1, "data": 1}
            ).sort([("_id", ASCENDING)]):
                d = doc.get("data")
                if not d:
                    continue
                cd = self.decode(d)
                state.update(cd)
                n += 1
                prev_size += len(cd)
            if not state:
                self.logger.info("Nothing to compact")
                return
            self.logger.info("Compacting %d log items (%d bytes)", n, prev_size)
            # Split to chunks when necessary
            bulk = []
            for c_data in self.iter_state_bulks(state):
                # t_mark += datetime.timedelta(seconds=1)
                # For more one slots raise condition with same t_mark
                # For that create random ObjectId
                bulk.append(InsertOne({"_id": ObjectId(), "slot": self.slot, "data": c_data}))
                nn += 1
                next_size += len(c_data)
        bulk.append(DeleteMany({"_id": {"$lte": t_mark_id}, "slot": self.slot}))
        await coll.bulk_write(bulk, ordered=True)
        self.logger.info(
            "Compacted to %d records (%d bytes). %.2f ratio",
            nn,
            next_size,
            float(prev_size) / float(next_size),
        )
