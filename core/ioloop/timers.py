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

# NOC modules
from noc.config import config


if config.features.use_uvlib:
    import pyuv
    from tornado.ioloop import IOLoop

    class PeriodicOffsetCallback(object):
        """Schedules the given callback to be called periodically
        with random offset.
        """

        def __init__(self, callback, callback_time):
            self.callback = callback
            if callback_time <= 0:
                raise ValueError("Periodic callback must have a positive callback_time")
            self.callback_time = callback_time
            self._timer = None

        def __del__(self):
            self.stop()

        def _run(self, h):
            if not self._timer:
                return
            try:
                return self.callback()
            except Exception:
                IOLoop.current().handle_callback_exception(self.callback)
            finally:
                IOLoop.current()._loop.update_time()

        def start(self):
            if not self._timer:
                self._timer = pyuv.Timer(IOLoop.current()._loop)
                self._timer.start(
                    self._run,
                    random.random() * self.callback_time / 1000.0,
                    self.callback_time / 1000.0,
                )

        def stop(self):
            if self._timer:
                self._timer.stop()
                self._timer = None

        def set_callback_time(self, callback_time):
            self.callback_time = callback_time
            if self._timer:
                self._timer.repeat = self.callback_time / 1000.0


else:

    class PeriodicCallback(object):
        def __init__(self, cb: Coroutine, interval: int, delay: int = 0):
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

        def set_interval(self, interval):
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
