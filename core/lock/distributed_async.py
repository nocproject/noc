# ----------------------------------------------------------------------
#  Distributed Async Lock
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2021 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List
import datetime
import random
from logging import getLogger
import asyncio

# Third-party modules
import pymongo
from pymongo.collection import Collection
from bson import ObjectId

# NOC modules
from noc.core.mongo.connection_async import get_db
from noc.core.perf import metrics
from .base import BaseLock, DEFAULT_TTL

DEFAULT_LOCK_WAIT = 1.0
DEFAULT_LOCK_WAIT_JITTER = 0.1

logger = getLogger(__name__)


class DistributedAsyncLock(BaseLock):
    """
    Distributed locking primitive for coroutines.
    Allows exclusive access to all requested items within category
    between the group of processes.

    Example
    -------
    ```
    lock = DistributedLock("test", "test:12")
    async with lock.acquire(["obj1", "obj2"]):
        ...
    ```
    """

    def __init__(self, category: str, owner: str, ttl: Optional[float] = None):
        """
        :param category: Lock category name
        :param owner: Lock owner id
        :param ttl: Default lock ttl in seconds
        """
        super().__init__(category, owner, ttl=ttl)
        self.collection = None

    def get_collection_name(self) -> str:
        """
        Get name of the lock collection
        """
        return f"locks.{self.category}"

    async def get_collection(self) -> Collection:
        """
        Ensure the collection is exists and indexed properly
        """
        if self.collection:
            return self.collection
        coll = get_db()[self.get_collection_name()]
        # Ensure indexes
        await coll.create_index([("items", pymongo.ASCENDING)], unique=True)
        await coll.create_index([("expires", pymongo.ASCENDING)], expireAfterSeconds=0)
        # Remove stale locks
        await coll.delete_many({"owner": self.owner})
        self.collection = coll
        return coll

    async def acquire_by_items(self, items: List[str], ttl: Optional[float] = None) -> str:
        """
        Acquire lock by list of items
        """
        coll = await self.get_collection()
        lock_id = ObjectId()
        ttl = ttl or self.ttl or DEFAULT_TTL
        metrics[f"lock_{self.category}_requests"] += 1
        logger.debug(
            "[%s|%s] Acquiring lock for %s (%s seconds)",
            self.category,
            self.owner,
            ", ".join(items),
            ttl,
        )
        while True:
            try:
                await coll.insert_one(
                    {
                        "_id": lock_id,
                        "items": items,
                        "owner": self.owner,
                        "expire": datetime.datetime.now() + datetime.timedelta(seconds=ttl),
                    }
                )
                return str(lock_id)
            except pymongo.errors.DuplicateKeyError:
                metrics[f"lock_{self.category}_misses"] += 1
                jitter = random.random() * DEFAULT_LOCK_WAIT_JITTER * DEFAULT_LOCK_WAIT
                timeout = DEFAULT_LOCK_WAIT + jitter
                logger.debug(
                    "[%s|%s] Cannnot get lock. Waiting %s seconds",
                    self.category,
                    self.owner,
                    timeout,
                )
                await asyncio.sleep(timeout)

    async def release_by_lock_id(self, lock_id: str):
        """
        Release lock by id
        """
        await self.collection.delete_one({"_id": ObjectId(lock_id)})
