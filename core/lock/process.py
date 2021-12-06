# ----------------------------------------------------------------------
#  Distributed Lock
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2021 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict, Set
from logging import getLogger
import itertools
from threading import Condition

# NOC modules
from noc.core.perf import metrics
from .base import BaseLock

logger = getLogger(__name__)


class ProcessLock(BaseLock):
    """
    Distributed locking primitive.
    Allows exclusive access to all requested items within category
    between the threads of single process.

    Example
    -------
    ```
    lock = ProcessLock("test", "test:12")
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
        super().__init__(category, owner, ttl=ttl)
        self.lock_id_seq = itertools.count()
        self.items: Dict[str, Set[str]] = {}
        self.items_condition = Condition()

    def acquire_by_items(self, items: List[str], ttl: Optional[float] = None) -> str:
        """
        Acquire lock by list of items
        """

        def is_ready():
            for locked in self.items.values():
                if locked.intersection(items_set):
                    metrics[f"lock_{self.category}_misses"] += 1
                    logger.debug(
                        "[%s|%s] Cannnot get lock. Waiting",
                        self.category,
                        self.owner,
                    )
                    return False
            return True

        metrics[f"lock_{self.category}_requests"] += 1
        lock_id = str(next(self.lock_id_seq))
        items_set = set(items)
        metrics[f"lock_{self.category}_requests"] += 1
        logger.debug(
            "[%s|%s] Acquiring lock for %s (%s seconds)",
            self.category,
            self.owner,
            ", ".join(items),
            ttl,
        )
        with self.items_condition:
            self.items_condition.wait_for(is_ready)
            self.items[lock_id] = items_set
        return lock_id

    def release_by_lock_id(self, lock_id: str):
        """
        Release lock by id
        """
        with self.items_condition:
            if lock_id in self.items:
                del self.items[lock_id]
            self.items_condition.notify()
