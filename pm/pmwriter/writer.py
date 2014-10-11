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
            batch = self.daemon.get_batch()
            n = batch.flush()
            logger.info("%d records flushed", n)
        logger.info("Stopping writer thread")
