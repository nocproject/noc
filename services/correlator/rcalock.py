# ----------------------------------------------------------------------
# RCALock class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import random
from typing import Optional
import datetime
import asyncio

# Third-party modules
import pymongo
from pymongo.errors import DuplicateKeyError

# NOC modules
from noc.config import config
from noc.core.mongo.connection import get_db
from noc.core.perf import metrics


class RCALock(object):
    """
    Lock set of items
    """

    COLL_NAME = "rcalocks"
    _coll: Optional[pymongo.collection.Collection] = None

    def __init__(self, items):
        self.items = items
        self.lock_id = None

    @classmethod
    def get_collection(cls) -> pymongo.collection:
        """
        Get pymongo collection instance
        :return:
        """
        if not cls._coll:
            cls._coll = get_db()[cls.COLL_NAME]
        return cls._coll

    @classmethod
    def create_indexes(cls) -> None:
        """
        Create necessary indexes
        :return:
        """
        coll = cls.get_collection()
        coll.create_index([("items", pymongo.ASCENDING)], unique=True)
        coll.create_index([("expires", pymongo.ASCENDING)], expireAfterSeconds=0)

    async def __aenter__(self) -> "RCALock":
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()

    async def acquire(self) -> None:
        def randomized(n: float) -> float:
            dev = config.correlator.rca_lock_dev
            return n * (1.0 - dev + 2.0 * dev * random.random())

        if not self.items:
            return
        t = config.correlator.rca_lock_initial_timeout
        max_timeout = config.correlator.rca_lock_max_timeout
        exp_delta = datetime.timedelta(seconds=config.correlator.rca_lock_expiry)
        coll = self.get_collection()
        while True:
            try:
                r = coll.insert_one(
                    {"items": self.items, "expires": datetime.datetime.utcnow() + exp_delta}
                )
                self.lock_id = r.inserted_id
                metrics["rca_lock_acquired"] += 1
                return
            except DuplicateKeyError:
                metrics["rca_locks_collisions"] += 1
                await asyncio.sleep(t)
                metrics["rca_locks_wait_ms"] += int(t * 1000)
                if t < max_timeout:
                    t = randomized(t * config.correlator.rca_lock_rate)
                    t = min(t, max_timeout)
                if t >= max_timeout:
                    t = randomized(max_timeout)

    async def release(self) -> None:
        if self.lock_id:
            metrics["rca_lock_released"] += 1
            self.get_collection().delete_one({"_id": self.lock_id})
            self.lock_id = None
