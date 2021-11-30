# ----------------------------------------------------------------------
#  Distributed Lock
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2021 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Optional, Iterable, List
import datetime
import time
import random
from logging import getLogger

# Third-party modules
import pymongo
from pymongo.collection import Collection
from bson import ObjectId

# NOC modules
from noc.core.mongo.connection import get_db
from noc.core.perf import metrics

DEFAULT_TTL = 60.0
DEFAULT_LOCK_WAIT = 1.0
DEFAULT_LOCK_WAIT_JITTER = 0.1

logger = getLogger(__name__)


class DistributedLock(object):
    """
    Distributed locking primitive.
    Allows exclusive access to all requested items within category.

    Example
    -------
    ```
    lock = DistributedLock("test", "test:12")
    with lock.acquire(["obj1", "obj2"]):
        ...
    ```
    """

    def __init__(self, category: str, owner: str, ttl: Optional[float] = None):
        """
        :param category: Lock category name
        :param owner: Lock owner id
        :param ttl: Default lock ttl in seconds
        """
        self.category = category
        self.owner = owner
        self.ttl = ttl
        self.collection = self.get_collection()
        self.release_all()

    def release_all(self):
        """
        Release all locks held by owner
        """
        self.collection.delete_many({"owner": self.owner})

    def get_collection_name(self) -> str:
        """
        Get name of the lock collection
        """
        return f"locks.{self.category}"

    def get_collection(self) -> Collection:
        """
        Ensure the collection is exists and indexed properly
        """
        coll = get_db()[self.get_collection_name()]
        coll.create_index([("items", pymongo.ASCENDING)], unique=True)
        coll.create_index([("expires", pymongo.ASCENDING)], expireAfterSeconds=0)
        return coll

    def acquire(self, items: Iterable[str], ttl: Optional[float] = None) -> "Token":
        """
        Acquire lock context manager.

        Example:

        ```
        with lock.acquire(["obj1", "ob2"]):
            ...
        ```
        """
        return Token(self, items, ttl=ttl)

    def acquire_by_items(self, items: List[str], ttl: Optional[float] = None) -> ObjectId:
        """
        Acquire lock by list of items
        """
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
                self.collection.insert_one(
                    {
                        "_id": lock_id,
                        "items": items,
                        "owner": self.owner,
                        "expire": datetime.datetime.now() + datetime.timedelta(seconds=ttl),
                    }
                )
                return lock_id
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
                time.sleep(timeout)

    def release_by_lock_id(self, lock_id: ObjectId):
        """
        Release lock by id
        """
        self.collection.delete_one({"_id": lock_id})


class Token(object):
    """
    Active lock context manager
    """

    def __init__(self, lock: DistributedLock, items: Iterable[str], ttl: Optional[float] = None):
        self.lock = lock
        self.items = list(items)
        self.ttl = ttl
        self.lock_id: Optional[ObjectId] = None

    def __enter__(self):
        self.lock_id = self.lock.acquire_by_items(self.items, ttl=self.ttl)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_id:
            self.lock.release_by_lock_id(self.lock_id)
