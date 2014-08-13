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


class Writer(threading.Thread):
    daemon = True

    def __init__(self, daemon, instance, storage_class):
        super(Writer, self).__init__(name="writer-%s" % instance)
        self.daemon = daemon
        self.instance = instance
        self.storage = storage_class()

    def info(self, msg):
        logging.info("[writer-%s] %s" % (self.instance, msg))

    def debug(self, msg):
        logging.debug("[writer-%s] %s" % (self.instance, msg))

    def error(self, msg):
        logging.error("[writer-%s] %s" % (self.instance, msg))

    def run(self):
        for metric, datapoints in self.daemon.cache.iter_metrics():
            self.debug("Writing %s %s" % (metric, datapoints))
            sr = self.daemon.get_storage_rule(metric)
            if not self.storage.exists(metric):
                self.info("Creating metric %s" % metric)
                try:
                    self.storage.create(metric, **sr)
                except Exception, why:
                    self.error("Failed to create metric %s: %s" % (
                        metric, why))
                    self.daemon.cache.release_metric(metric)
                    continue
                self.info("Done")
            try:
                self.storage.write(metric, datapoints)
            except Exception, why:
                self.error("Failed to write metric %s: %s" % (
                    metric, why))
            self.daemon.cache.release_metric(metric)
        self.info("Stopping")
