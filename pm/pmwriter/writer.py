## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Writer daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import threading
## NOC modules

logger = logging.getLogger(__name__)


class Writer(threading.Thread):
    daemon = True

    def __init__(self, daemon):
        super(Writer, self).__init__(name="writer")
        self.daemon = daemon

    def run(self):
        logger.info("Running writer thread")
        while True:
            self.daemon.metrics.db_flush_ops += 1
            with self.daemon.metrics.db_flush_time.timer():
                batch = self.daemon.get_batch()
                n = batch.flush()
            logger.info("%d records flushed", n)
            self.daemon.metrics.db_flush_records += n
        logger.info("Stopping writer thread")
