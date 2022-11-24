# ----------------------------------------------------------------------
# Various ioloop timers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import random
import asyncio
import math

# Third-party modules
from typing import Optional, Coroutine


class PeriodicCallback(object):
    def __init__(self, cb: Coroutine, interval: int, delay: int = 0):
        """
        This function sets up a timer that will run the coroutine every
        interval miliseconds, starting after delay seconds

        :param cb: The coroutine to call
        :type cb: Coroutine
        :param interval: The interval in milliseconds between each call of the callback
        :type interval: int
        :param delay: The delay before the first call to the callback, defaults to 0
        :type delay: int (optional)
        """
        self.cb = cb
        self.interval = float(interval) / 1000.0
        self.delay = float(delay) / 1000.0
        self._running = False
        self._timer: Optional[asyncio.TimerHandle] = None
        self._start_time: Optional[float] = None

    def start(self):
        self._running = True
        self._schedule_next()

    def stop(self):
        self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def set_interval(self, interval: int):
        self.interval = float(interval) / 1000.0
        if self._running and self._timer:
            self._timer.cancel()
            self._timer = None
            self._schedule_next()

    def _run(self):
        self._timer = None
        try:
            asyncio.ensure_future(self.cb())
        finally:
            self._schedule_next()

    def _schedule_next(self):
        loop = asyncio.get_running_loop()
        now = loop.time()
        if self._start_time is None:
            # First run
            when = now + self.delay
            self._start_time = when
        else:
            when = (
                self._start_time
                + (math.floor((now - self._start_time) / self.interval) + 1.0) * self.interval
            )
        self._timer = asyncio.get_running_loop().call_at(when, self._run)


class PeriodicOffsetCallback(PeriodicCallback):
    def __init__(self, cb: Coroutine, interval: int):
        super().__init__(cb, interval, random.random() * interval)
