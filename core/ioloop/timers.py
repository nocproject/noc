# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various ioloop timers
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import random
## Third-party modules
from tornado.ioloop import PeriodicCallback


class PeriodicOffsetCallback(PeriodicCallback):
    """Schedules the given callback to be called periodically
    with random offset.
    """
    def start(self):
        """Starts the timer."""
        self._running = True
        self._next_timeout = self.io_loop.time()
        self._schedule_first()

    def _schedule_first(self):
        if self._running:
            self._next_timeout += int(random.random() *
                                      self.callback_time / 1000.0)
            self._timeout = self.io_loop.add_timeout(
                self._next_timeout,
                self._run
            )

    def set_callback_time(self, callback_time):
        self.callback_time = callback_time
