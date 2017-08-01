#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# chwriter service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import tornado.ioloop
import tornado.gen
# NOC modules
from noc.core.service.base import Service
from noc.core.http.client import fetch
from channel import Channel
from noc.core.perf import metrics
from noc.config import config


class CHWriterService(Service):
    name = "chwriter"

    def __init__(self):
        super(CHWriterService, self).__init__()
        self.channels = {}
        self.last_ts = None
        self.last_metrics = 0
        self.table_fields = {}  # table name -> fields
        self.last_columns = 0
        self.is_sharded = False
        if config.clickhouse.cluster and config.chwriter.write_to:
            # Distributed configuration
            self.topic = "chwriter-%s" % (config.chwriter.write_to.replace(":", "-"))
            self.ch_address = config.chwriter.write_to
        else:
            # Standalone configuration
            self.topic = "chwriter"
            self.ch_address = config.clickhouse.addresses[0]

    @tornado.gen.coroutine
    def on_activate(self):
        report_callback = tornado.ioloop.PeriodicCallback(
            self.report, 10000, self.ioloop
        )
        report_callback.start()
        check_callback = tornado.ioloop.PeriodicCallback(
            self.check_channels, config.chwriter.batch_delay_ms,
            self.ioloop
        )
        check_callback.start()
        self.subscribe(
            self.topic,
            "chwriter",
            self.on_data,
            raw=True,
            max_backoff_duration=3
        )

    def get_channel(self, fields):
        if fields not in self.channels:
            self.channels[fields] = Channel(
                self,
                fields,
                self.ch_address,
                config.clickhouse.db
            )
            metrics["channels_active"] += 1
        return self.channels[fields]

    def on_data(self, message, records, *args, **kwargs):
        """
        Called on new dispose message
        Message format
        <table>.<field1>. .. .<fieldN>\n
        <v1>\t...\t<vN>\n
        ...
        <v1>\t...\t<vN>\n
        """
        if metrics["records_buffered"].value > config.chwriter.records_buffer:
            self.logger.info(
                "Input buffer is full (%s/%s). Deferring message",
                metrics["records_buffered"].value,
                config.chwriter.records_buffer
            )
            metrics["deferred_messages"] += 1
            return False
        fields, data = records.split("\n", 1)
        channel = self.get_channel(fields)
        n = channel.feed(data)
        metrics["records_received"] += n
        metrics["records_buffered"] += n
        return True

    @tornado.gen.coroutine
    def report(self):
        nm = metrics["records_written"].value
        t = self.ioloop.time()
        if self.last_ts:
            speed = float(nm - self.last_metrics) / (t - self.last_ts)
            self.logger.info(
                "Feeding speed: %.2frecords/sec, active channels: %s, buffered records: %d",
                speed,
                metrics["channels_active"],
                metrics["records_buffered"].value
            )
        self.last_metrics = nm
        self.last_ts = t

    @tornado.gen.coroutine
    def check_channels(self):
        expired = [c for c in self.channels if self.channels[c].is_expired()]
        for x in expired:
            self.logger.info("Closing expired channel %s", x)
            del self.channels[x]
        metrics["channels_active"] = len(self.channels)
        for c in list(self.channels):
            channel = self.channels.get(c)
            if channel and channel.is_ready():
                yield self.flush_channel(channel)

    @tornado.gen.coroutine
    def flush_channel(self, channel):
        channel.start_flushing()
        n = channel.n
        data = channel.get_data()
        for i in range(10):
            t0 = self.ioloop.time()
            self.logger.debug("[%s] Sending %s records", channel.name, n)
            written = False
            try:
                code, headers, body = yield fetch(
                    channel.url,
                    method="POST",
                    body=data,
                    content_encoding=config.clickhouse.encoding
                )
                if code == 200:
                    self.logger.info(
                        "[%s] %d records sent in %.2fms",
                        channel.name,
                        n, (self.ioloop.time() - t0) * 1000
                    )
                    metrics["records_written"] += n
                    metrics["records_buffered"] -= n
                    channel.stop_flushing()
                    written = True
                elif code in (598, 599):
                    self.logger.info(
                        "[%s] Timed out: %s",
                        channel.name, body
                    )
                    metrics["records_spool_timeouts"] += 1
                else:
                    self.logger.info(
                        "[%s] Failed to write records: %s %s",
                        channel.name,
                        code, body
                    )
                    metrics["records_spool_failed"] += 1
            except Exception as e:
                self.logger.error(
                    "[%s] Failed to spool %d records due to unknown error: %s",
                    channel.name, n, e
                )
            if written:
                raise tornado.gen.Return()
            timeout = 1.0
            self.logger.info(
                "Clickhouse is getting ill. "
                "Giving chance to recover. Waiting for %.2fms",
                timeout * 1000
            )
            metrics["slept_time"] += int(timeout)
            yield tornado.gen.sleep(timeout)
        self.logger.info("[%s] Recovering records", channel.name)
        channel.recover(n, data)
        channel.stop_flushing()


if __name__ == "__main__":
    CHWriterService().start()
