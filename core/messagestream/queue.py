# ----------------------------------------------------------------------
# MessageStream Queue
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import deque
from threading import Lock
import asyncio
from typing import Optional, Dict, Any
from .message import PublishRequest


class MessageStreamQueue(object):
    def __init__(self, loop: Optional[asyncio.BaseEventLoop] = None):
        self.queue: deque = deque()
        self.lock = Lock()
        self.waiter: Optional[asyncio.Event] = None
        self.drain_waiter: Optional[asyncio.Event] = None
        self.loop: Optional[asyncio.BaseEventLoop] = loop
        self.req_puts: int = 0
        self.req_gets: int = 0
        self.to_shutdown: bool = False

    def _notify_waiter(self, waiter: asyncio.Event) -> None:
        if self.loop:
            self.loop.call_soon_threadsafe(waiter.set)
        else:
            waiter.set()

    def put(self, req: PublishRequest, fifo: bool = True) -> None:
        """
        Put request into queue
        :param req:
        :param fifo:
        :return:
        """
        with self.lock:
            if fifo:
                self.queue.append(req)
            else:
                self.queue.appendleft(req)
            self.req_puts += 1
            # Notify waiters
            if not self.waiter:
                return
            self._notify_waiter(self.waiter)

    async def get(self, timeout: Optional[float] = None):
        """
        Get request from queue. Wait forever, if timeout is None,
        of return None if timeout is expired.
        :param timeout:
        :return:
        """
        with self.lock:
            # Direct path, in case the queue is not empty
            if len(self.queue):
                self.req_gets += 1
                return self.queue.popleft()
            self.waiter = asyncio.Event()
        # Wait until waiter is set
        if timeout:
            try:
                await asyncio.wait_for(self.waiter.wait(), timeout)
            except asyncio.TimeoutError:
                return None
        else:
            await self.waiter.wait()
        # Pop message and reset waiter
        with self.lock:
            if self.drain_waiter and not len(self.queue):
                self._notify_waiter(self.drain_waiter)
            self.waiter = None
            self.req_gets += 1
            try:
                return self.queue.popleft()
            except IndexError:
                return None  # Triggered by shutdown

    def apply_metrics(self, data: Dict[str, Any]) -> None:
        data.update(
            {
                "liftbridge_publish_puts": self.req_puts,
                "liftbridge_publish_gets": self.req_gets,
                "liftbridge_publish_queue": len(self.queue),
            }
        )

    def shutdown(self) -> None:
        with self.lock:
            if self.waiter:
                self._notify_waiter(self.waiter)
        self.to_shutdown = True

    async def drain(self, timeout: Optional[float] = None) -> bool:
        """
        Wait until queue is empty
        :return:
        """
        with self.lock:
            if self.waiter:
                self._notify_waiter(self.waiter)
        if not len(self.queue):
            return True
        self.drain_waiter = asyncio.Event()
        if timeout:
            try:
                await asyncio.wait_for(self.drain_waiter.wait(), timeout)
            except asyncio.TimeoutError:
                pass
        else:
            await self.drain_waiter.wait()
        self.drain_waiter = None
        return len(self.queue) == 0

    def qsize(self) -> int:
        with self.lock:
            return len(self.queue)
