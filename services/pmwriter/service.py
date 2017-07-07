#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# pmwriter service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time
# Third-party modules
import tornado.ioloop
import tornado.gen
# NOC modules
from noc.config import config
from noc.core.service.base import Service
from noc.core.http.client import fetch


class PMWriterService(Service):
    name = "pmwriter"
    process_name = "noc-%(name).10s-%(instance).3s"

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
        return config.pmwriter.write_to, config.pmwriter.read_from

    def on_metric(self, message, metrics, *args, **kwargs):
        """
        Called on new dispose message
        """
        l = len(self.buffer)
        data = metrics.splitlines()
        ld = len(data)
        self.perf_metrics["metrics_received"] += ld
        if l < config.pmwriter.metrics_buffer:
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
                    l, config.pmwriter.metrics_buffer
                )
                self.overrun_start = time.time()
            self.perf_metrics["metrics_deferred"] += ld
            return False

    @tornado.gen.coroutine
    def write_metrics(self):
        self.logger.info(
            "Starting message sender. Batch size %d. Metrics buffer %d",
            config.pmwriter.batch_size,
            config.pmwriter.metrics_buffer
        )
        bs = config.pmwriter.batch_size
        while True:
            if not self.buffer:
                self.perf_metrics["slept_time"] += int(self.MAX_DELAY)
                yield tornado.gen.sleep(self.MAX_DELAY)
                continue
            if len(self.buffer) < bs and self.speed:
                sleep_time = int((bs - len(self.buffer)) / self.speed)
                if sleep_time > self.MAX_DELAY:
                    sleep_time = int(self.MAX_DELAY)
                self.logger.info("Waiting for buffer for %f seconds. Current buff size %d",
                                 sleep_time, len(self.buffer))
                self.perf_metrics["slept_time"] += sleep_time
                yield tornado.gen.sleep(sleep_time)
            batch, self.buffer = self.buffer[:bs], self.buffer[bs:]
            data = "\n".join(batch)
            while True:
                t0 = self.ioloop.time()
                self.logger.debug("Sending %d metrics", len(batch))
                client = tornado.httpclient.AsyncHTTPClient()
                try:
                    response = yield client.fetch(
                        # Configurable database name
                        "http://%s/write?db=%s&precision=s" % (
                            self.influx,
                            config.pmwriter.influx_db
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
                        self.perf_metrics["metrics_spool_failed"] += 1
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
                self.perf_metrics["slept_time"] += int(timeout)
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
                "Feeding speed: %.2fmetrics/sec, buffer size %d", self.speed, len(self.buffer)
            )
        self.last_metrics = nm
        self.last_ts = t


if __name__ == "__main__":
    PMWriterService().start()
