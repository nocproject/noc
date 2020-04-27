# ----------------------------------------------------------------------
# Various ioloop timers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import random

# Third-party modules
from tornado.ioloop import IOLoop, PeriodicCallback
from noc.config import config


if config.features.use_uvlib:
    import pyuv

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

    class PeriodicOffsetCallback(PeriodicCallback):
        """Schedules the given callback to be called periodically
        with random offset.
        """

        def start(self):
            """Starts the timer."""
            self._running = True
            io_loop = IOLoop.current()
            self._next_timeout = io_loop.time() + random.random() * self.callback_time / 1000.0
            self._timeout = io_loop.add_timeout(self._next_timeout, self._run)

        def set_callback_time(self, callback_time):
            self.callback_time = callback_time
