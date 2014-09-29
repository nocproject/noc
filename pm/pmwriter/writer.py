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
from noc.lib.perf import MetricsHub

logger = logging.getLogger(__name__)


class Writer(threading.Thread):
    daemon = True

    def __init__(self, daemon, instance, storage_class):
        super(Writer, self).__init__(name="writer-%s" % instance)
        self.daemon = daemon
        self.instance = instance
        self.storage = storage_class()
        self.logger = PrefixLoggerAdapter(logger, "writer-%d" % instance)
        mprefix = "noc.noc-pmwriter.%s.writer.%s" % (
            self.daemon.instance_id, self.instance)
        self.metrics = MetricsHub(
            mprefix,
            "new.created", "new.failed", "new.throttled",
            "new.time",
            "write.success", "write.failed", "write.time",
            "srlookup.lookups", "srlookup.time"
        )

    def run(self):
        self.logger.info("Running writer thread")
        for metric, datapoints in self.daemon.cache.iter_metrics():
            t0 = time.time()
            with self.metrics.srlookup_time.timer():
                sr = self.daemon.get_storage_rule(metric)
                self.metrics.srlookup_lookups += 1
            if self.storage.EXPLICIT_CREATE and not self.storage.exists(metric):
                if not self.daemon.can_create_metric():
                    self.metrics.new_throttled += 1
                    self.logger.info(
                        "Throttling metric '%s' creation. Discarding data",
                        metric
                    )
                    continue
                self.logger.info("Creating metric %s", metric)
                try:
                    with self.metrics.new_time.timer():
                        self.storage.create(metric, **sr)
                except Exception, why:
                    self.logger.error("Failed to create metric %s: %s",
                                      metric, why)
                    self.daemon.cache.release_metric(metric)
                    self.metrics.new_failed += 1
                    continue
                self.metrics.new_created += 1
                self.logger.info("Metric created: '%s'", metric)
            try:
                with self.metrics.write_time.timer():
                    self.storage.write(metric, datapoints, sr)
                self.metrics.write_success += 1
            except Exception, why:
                self.logger.error("Failed to write metric %s: %s",
                                  metric, why)
                self.metrics.write_failed += 1
            self.daemon.cache.release_metric(metric)
            self.storage.flush()
            self.logger.debug("Writing %s %s (%.2fms)",
                              metric, datapoints,
                              (time.time() - t0) * 1000)
        self.logger.info("Stopping writer thread")
