#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# chwriter service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
# Third-party modules
import tornado.ioloop
import tornado.gen
import tornado.httpclient
# NOC modules
from noc.core.service.base import Service
from channel import Channel


class CHWriterService(Service):
    name = "chwriter"
    process_name = "noc-%(name).10s-%(instance).3s"

    HOST = os.environ.get("NOC_CLICKHOUSE_HOST", "clickhouse")
    PORT = os.environ.get("NOC_CLICKHOUSE_PORT", 8123)
    DB = os.environ.get("NOC_CLICKHOUSE_DB", "noc")

    def __init__(self):
        super(CHWriterService, self).__init__()
        self.channels = {}
        self.last_ts = None
        self.last_metrics = 0
        self.table_fields = {}  # table name -> fields
        self.last_columns = 0

    @tornado.gen.coroutine
    def on_activate(self):
        report_callback = tornado.ioloop.PeriodicCallback(
            self.report, 10000, self.ioloop
        )
        report_callback.start()
        check_callback = tornado.ioloop.PeriodicCallback(
            self.check_channels, self.config.batch_delay_ms, self.ioloop
        )
        check_callback.start()
        self.subscribe(
            "chwriter",
            "chwriter",
            self.on_data,
            raw=True,
            max_backoff_duration=3
        )

    def get_channel(self, fields):
        if fields not in self.channels:
            self.channels[fields] = Channel(self, fields)
            self.perf_metrics["channels_active"] += 1
        return self.channels[fields]

    def on_data(self, message, metrics, *args, **kwargs):
        """
        Called on new dispose message
        Message format
        <table>.<field1>. .. .<fieldN>\n
        <v1>\t...\t<vN>\n
        ...
        <v1>\t...\t<vN>\n
        """
        if self.perf_metrics["records_buffered"].value > self.config.records_buffer:
            self.perf_metrics["deferred_messages"] += 1
            return False
        fields, data = metrics.split("\n", 1)
        channel = self.get_channel(fields)
        n = channel.feed(data)
        self.perf_metrics["records_received"] += n
        self.perf_metrics["records_buffered"] += n
        return True

    @tornado.gen.coroutine
    def report(self):
        nm = self.perf_metrics["records_written"].value
        t = self.ioloop.time()
        if self.last_ts:
            speed = float(nm - self.last_metrics) / (t - self.last_ts)
            self.logger.info(
                "Feeding speed: %.2frecords/sec, active channels: %s, buffered records: %d",
                speed,
                self.perf_metrics["channels_active"],
                self.perf_metrics["records_buffered"].value
            )
        self.last_metrics = nm
        self.last_ts = t

    @tornado.gen.coroutine
    def check_channels(self):
        expired = [c for c in self.channels if self.channels[c].is_expired()]
        for x in expired:
            self.logger.info("Closing expired channel %s", x)
            del self.channels[x]
        self.perf_metrics["channels_active"] = len(self.channels)
        for c in self.channels:
            channel = self.channels[c]
            if channel.is_ready():
                yield self.flush_channel(channel)

    @tornado.gen.coroutine
    def flush_channel(self, channel):
        channel.start_flushing()
        n = channel.n
        data = channel.get_data()
        for i in range(10):
            t0 = self.ioloop.time()
            self.logger.debug("Sending %d records to channel %s", n, channel.name)
            client = tornado.httpclient.AsyncHTTPClient()
            written = False
            try:
                response = yield client.fetch(
                    "http://%s:%s/?database=%s&query=%s" % (
                        self.HOST, self.PORT, self.DB,
                        channel.get_encoded_insert_sql()),
                    method="POST",
                    body=data
                )
                if response.code == 200:
                    self.logger.info(
                        "%d metrics sent in %.2fms",
                        n, (self.ioloop.time() - t0) * 1000
                    )
                    self.perf_metrics["records_written"] += n
                    self.perf_metrics["records_buffered"] -= n
                    channel.stop_flushing()
                    written = True
                else:
                    self.logger.info(
                        "Failed to write metrics: %s",
                        response.body
                    )
                    self.perf_metrics["records_spool_failed"] += 1
            except tornado.httpclient.HTTPError as e:
                self.logger.error("Failed to spool %d records: %s",
                                  n, e)
            except Exception as e:
                self.logger.error(
                    "Failed to spool %d records due to unknown error: %s",
                    n, e
                )
            if written:
                raise tornado.gen.Return()
            timeout = 1.0
            self.logger.info(
                "Clickhouse is getting ill. "
                "Giving chance to recover. Waiting for %.2fms",
                timeout * 1000
            )
            self.perf_metrics["slept_time"] += int(timeout)
            yield tornado.gen.sleep(timeout)
        self.logger.info("Recovering records")
        channel.recover(n, data)
        channel.stop_flushing()

if __name__ == "__main__":
    CHWriterService().start()
