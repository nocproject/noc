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
import time
## NOC modules
from noc.lib.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)


class Writer(threading.Thread):
    daemon = True

    def __init__(self, daemon, instance, storage_class):
        super(Writer, self).__init__(name="writer-%s" % instance)
        self.daemon = daemon
        self.instance = instance
        self.storage = storage_class()
        self.logger = PrefixLoggerAdapter(logger, "writer-%d" % instance)

    def run(self):
        self.logger.info("Running writer thread")
        for metric, datapoints in self.daemon.cache.iter_metrics():
            t0 = time.time()
            sr = self.daemon.get_storage_rule(metric)
            if self.storage.EXPLICIT_CREATE and not self.storage.exists(metric):
                if not self.daemon.can_create_metric():
                    self.logger.info(
                        "Throttling metric '%s' creation. Discarding data",
                        metric
                    )
                    continue
                self.logger.info("Creating metric %s", metric)
                try:
                    self.storage.create(metric, **sr)
                except Exception, why:
                    self.logger.error("Failed to create metric %s: %s",
                                      metric, why)
                    self.daemon.cache.release_metric(metric)
                    continue
                self.logger.info("Metric created: '%s'", metric)
            try:
                self.storage.write(metric, datapoints, sr)
            except Exception, why:
                self.logger.error("Failed to write metric %s: %s",
                                  metric, why)
            self.daemon.cache.release_metric(metric)
            self.storage.flush()
            self.logger.debug("Writing %s %s (%.2fms)", metric, datapoints, (time.time() - t0) * 1000)
        self.logger.info("Stopping writer thread")
