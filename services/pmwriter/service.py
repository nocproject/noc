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
## NOC modules
from noc.core.service.base import Service
import noc.core.service.httpclient


class PMWriterService(Service):
    name = "pmwriter"
    process_name = "noc-%(name).10s-%(instance).2s"

    MAX_DELAY = 1.0

    def __init__(self):
        super(PMWriterService, self).__init__()
        self.influx = None
        self.last_ts = None
        self.last_metrics = 0
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
        self.ioloop.add_callback(self.write_metrics)
        self.influx, channel = self.get_topic()
        self.logger.info("Listening metrics/%s. Writing to %s",
                         channel, self.influx)
        self.subscribe(
            "metrics",
            channel,
            self.on_metric,
            raw=True,
            max_backoff_duration=3
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
        data = metrics.splitlines()
        ld = len(data)
        self.perf_metrics["metrics_received"] += ld
        if l < self.config.metrics_buffer:
            if self.overrun_start:
                dt = time.time() - self.overrun_start
                self.logger.info(
                    "Resuming message reading after %.2fms",
                    dt * 1000.0
                )
                self.overrun_start = None
            self.buffer += data
            return True
        else:
            if not self.overrun_start:
                self.logger.info(
                    "Temporary buffer overrun. "
                    "Suspending message reading (%s/%s)",
                    l, self.config.metrics_buffer
                )
                self.overrun_start = time.time()
            self.perf_metrics["metrics_deferred"] += ld
            return False

    @tornado.gen.coroutine
    def write_metrics(self):
        self.logger.info(
            "Starting message sender. Batch size %d. Metrics buffer %d",
            self.config.batch_size,
            self.config.metrics_buffer
        )
        bs = self.config.batch_size
        while True:
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
                        self.perf_metrics["metrics_written"] += len(batch)
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
        # Not reachable
        self.logger.error("Terminating message sender")

    @tornado.gen.coroutine
    def report(self):
        nm = self.perf_metrics["metrics_written"].value
        t = self.ioloop.time()
        if self.last_ts:
            self.speed = float(nm - self.last_metrics) / (t - self.last_ts)
            self.logger.info(
                "Feeding speed: %.2fmetrics/sec", self.speed
            )
        self.last_metrics = nm
        self.last_ts = t

if __name__ == "__main__":
    PMWriterService().start()
