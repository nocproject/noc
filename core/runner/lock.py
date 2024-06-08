# ---------------------------------------------------------------------
# LockManager implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import asyncio
from typing import Dict, Iterable, List
from dataclasses import dataclass


@dataclass
class _Waiter(object):
    lock: asyncio.Lock
    waiters: int = 0


class LockManager(object):
    def __init__(self):
        self._lock = asyncio.Lock()
        self._waiters: Dict[str, _Waiter] = {}

    def acquire(self, locks: Iterable[str]) -> "LockCtx":
        return LockCtx(self, sorted(set(locks)))

    async def _acquire(self, names: List[str]) -> None:
        locks: List[asyncio.Lock] = []
        async with self._lock:
            for name in names:
                waiter = self._waiters.get(name)
                if not waiter:
                    waiter = _Waiter(asyncio.Lock())
                    self._waiters[name] = waiter
                waiter.waiters += 1
                locks.append(waiter.lock)
        for lock in locks:
            await lock.acquire()

    async def _release(self, names: List[str]) -> None:
        async with self._lock:
            for name in names:
                waiter = self._waiters[name]
                waiter.waiters -= 1
                waiter.lock.release()
                if not waiter.waiters:
                    del self._waiters[name]  # No longer needed


class LockCtx(object):
    def __init__(self, parent: LockManager, names: Iterable[str]):
        self._parent = parent
        self._names = list(names)

    async def __aenter__(self) -> None:
        await self._parent._acquire(self._names)

    async def __aexit__(self, *args) -> None:
        await self._parent._release(self._names)
