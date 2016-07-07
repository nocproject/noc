#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pmwriter service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
# Third-party modules
import tornado.ioloop
import tornado.gen
import tornado.httpclient
import tornado.queues
## NOC modules
from noc.core.service.base import Service
import noc.core.service.httpclient


class PMWriterService(Service):
    name = "pmwriter"
    process_name = "noc-%(name).10s-%(instance).2s"

    MAX_DELAY = 1.0

    def __init__(self):
        super(PMWriterService, self).__init__()
        self.queue = None
        self.influx = None
        self.last_ts = None
        self.last_metrics = 0
        self.n_metrics = 0
        self.buffer = []
        self.speed = None
        self.overrun_start = None

    @tornado.gen.coroutine
    def on_activate(self):
        self.last_ts = self.ioloop.time()
        report_callback = tornado.ioloop.PeriodicCallback(
            self.report, 10000, self.ioloop
        )
        report_callback.start()
        self.queue = tornado.queues.Queue(maxsize=self.config.batch_size * 4)
        self.influx, channel = self.get_topic()
        self.logger.info("Listening metrics/%s. Writing to %s",
                         channel, self.influx)
        self.subscribe(
            "metrics",
            channel,
            self.on_metric,
            raw=True
        )
        self.ioloop.spawn_callback(self.send_metrics)

    def get_topic(self):
        """
        Returns influx service, channel name
        """
        # Influx affinity
        node_addr = self.config.listen.split(":")[0]
        influx = None
        channel = "pmwriter-%s" % node_addr
        for s in self.config.get_service("influxdb"):
            if s.split(":")[0] == node_addr:
                influx = s
                break
        if not influx:
            # Fallback to default
            influx = self.resolve_service("influxdb", 1)[0]
            channel = "pmwriter"
        return influx, channel

    def on_metric(self, message, metrics, *args, **kwargs):
        """
        Called on new dispose message
        """
        l = len(self.buffer)
        ms = self.config.batch_size * 2
        if l < ms:
            if self.overrun_start:
                dt = time.time() - self.overrun_start
                self.logger.info(
                    "Resuming message reading after %.2fms",
                    dt * 1000.0
                )
                self.overrun_start = None
            self.buffer += metrics.splitlines()
            return True
        else:
            if not self.overrun_start:
                self.logger.info(
                    "Temporary buffer overrun. "
                    "Suspending message reading (%s/%s)",
                    l, ms
                )
                self.overrun_start = time.time()
            return False

    @tornado.gen.coroutine
    def send_metrics(self):
        self.logger.info("Starting message sender")
        while True:
            bs = self.config.batch_size
            if not self.buffer:
                yield tornado.gen.sleep(self.MAX_DELAY)
                continue
            if len(self.buffer) < bs and self.speed:
                yield tornado.gen.sleep((bs - len(self.buffer)) / self.speed)
            batch, self.buffer = self.buffer[:bs], self.buffer[bs:]
            body = "\n".join(batch)
            while True:
                t0 = self.ioloop.time()
                self.logger.debug("Sending %d metrics", len(batch))
                client = tornado.httpclient.AsyncHTTPClient()
                try:
                    response = yield client.fetch(
                        # Configurable database name
                        "http://%s/write?db=%s&precision=s" % (
                            self.influx,
                            self.config.influx_db
                        ),
                        method="POST",
                        body=body
                    )
                    # @todo: Check for 204
                    if response.code == 204:
                        self.logger.info(
                            "%d metrics sent in %.2fms",
                            len(batch), (self.ioloop.time() - t0) * 1000
                        )
                        self.n_metrics += len(batch)
                        break
                    else:
                        self.logger.info(
                            "Failed to write metrics: %s",
                            response.body
                        )
                except tornado.httpclient.HTTPError as e:
                    self.logger.error("Failed to spool %d metrics: %s",
                                      len(batch), e)
                except Exception as e:
                    self.logger.error(
                        "Failed to spool %d metrics due to unknown error: %s",
                        len(batch), e
                    )
                timeout = 1.0
                self.logger.info(
                    "InfluxDB is getting ill. "
                    "Giving chance to recover. Waiting for %.2fms",
                    timeout * 1000
                )
                yield tornado.gen.sleep(timeout)

    @tornado.gen.coroutine
    def report(self):
        t = self.ioloop.time()
        if self.last_ts:
            self.speed = float(self.n_metrics - self.last_metrics) / (t - self.last_ts)
            self.logger.info(
                "Feeding speed: %.2fmetrics/sec", self.speed
            )
        self.last_metrics = self.n_metrics
        self.last_ts = t

if __name__ == "__main__":
    PMWriterService().start()
