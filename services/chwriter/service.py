#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# chwriter service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import tornado.ioloop
import tornado.gen

# NOC modules
from noc.core.service.base import Service
from noc.core.http.client import fetch
from noc.config import config
from noc.core.perf import metrics
from noc.services.chwriter.channel import Channel
from noc.core.backport.time import perf_counter
from noc.core.comp import smart_text


class CHWriterService(Service):
    name = "chwriter"

    CH_SUSPEND_ERRORS = {598, 599}

    def __init__(self):
        super(CHWriterService, self).__init__()
        self.channels = {}
        self.last_ts = None
        self.last_metrics = 0
        self.table_fields = {}  # table name -> fields
        self.last_columns = 0
        self.is_sharded = False
        self.stopping = False
        if config.clickhouse.cluster and config.chwriter.write_to:
            # Distributed configuration
            self.ch_address = config.chwriter.write_to
        else:
            # Standalone configuration
            self.ch_address = config.clickhouse.rw_addresses[0]
        self.restore_timeout = None

    @tornado.gen.coroutine
    def on_activate(self):
        report_callback = tornado.ioloop.PeriodicCallback(self.report, 10000, self.ioloop)
        report_callback.start()
        check_callback = tornado.ioloop.PeriodicCallback(
            self.check_channels, config.chwriter.batch_delay_ms, self.ioloop
        )
        check_callback.start()
        self.subscribe(
            config.chwriter.topic,
            "chwriter",
            self.on_data,
            raw=True,
            max_backoff_duration=3,
            max_in_flight=config.chwriter.max_in_flight,
        )
        self.logger.info("Sending records to %s" % self.ch_address)

    def get_channel(self, table):
        if table not in self.channels:
            self.channels[table] = Channel(self, table, self.ch_address, config.clickhouse.db)
            metrics["channels_active"] += 1
        return self.channels[table]

    def on_data(self, message, records, *args, **kwargs):
        """
        Called on new dispose message
        Message format
        <table>.<field1>. .. .<fieldN>\n
        <v1>\t...\t<vN>\n
        ...
        <v1>\t...\t<vN>\n
        """
        if self.stopping:
            self.logger.info("Message received during stopping, requeueing message")
            return False
        if self.restore_timeout:
            self.logger.info("ClickHouse is not available, requeueing message")
            return False
        if metrics["records_buffered"].value > config.chwriter.records_buffer:
            self.logger.info(
                "Input buffer is full (%s/%s). Deferring message",
                metrics["records_buffered"].value,
                config.chwriter.records_buffer,
            )
            metrics["deferred_messages"] += 1
            return False
        table, data = smart_text(records).split("\n", 1)
        self.logger.debug("Receiving %s", table)
        if "." in table or "|" in table:
            self.logger.error("Message in legacy format dropped: %s" % table)
            metrics["dropped_legacy_messages"] += 1
            return True
        channel = self.get_channel(table)
        n = channel.feed(data)
        metrics["records_received"] += n
        metrics["records_buffered"] += n
        return True

    @tornado.gen.coroutine
    def report(self):
        nm = metrics["records_written"].value
        t = perf_counter()
        if self.last_ts:
            speed = float(nm - self.last_metrics) / (t - self.last_ts)
            self.logger.info(
                "Feeding speed: %.2frecords/sec, active channels: %s, buffered records: %d",
                speed,
                metrics["channels_active"].value,
                metrics["records_buffered"].value,
            )
        self.last_metrics = nm
        self.last_ts = t

    @tornado.gen.coroutine
    def check_channels(self):
        expired = [c for c in self.channels if self.channels[c].is_expired()]
        for x in expired:
            self.logger.info("Closing expired channel %s", x)
            del self.channels[x]
            metrics["channels_active"].value = len(self.channels)
        self.logger.debug(
            "Active channels: %s", ", ".join(self.channels[c].name for c in self.channels)
        )
        for c in list(self.channels):
            if self.restore_timeout:
                break
            channel = self.channels.get(c)
            if channel:
                self.logger.debug(
                    "Channel %s: ready=%s flushing=%s",
                    channel.name,
                    channel.is_ready(),
                    channel.flushing,
                )
            if channel and channel.is_ready():
                yield self.flush_channel(channel)

    @tornado.gen.coroutine
    def flush_channel(self, channel):
        channel.start_flushing()
        n = channel.n
        data = channel.get_data()
        t0 = perf_counter()
        self.logger.debug("[%s] Sending %s records", channel.name, n)
        written = False
        suspended = False
        try:
            code, headers, body = yield fetch(
                channel.url,
                method="POST",
                body=data,
                user=config.clickhouse.rw_user,
                password=config.clickhouse.rw_password or "",
                content_encoding=config.clickhouse.encoding,
            )
            if code == 200:
                self.logger.info(
                    "[%s] %d records sent in %.2fms", channel.name, n, (perf_counter() - t0) * 1000
                )
                metrics["records_written"] += n
                metrics["records_buffered"] -= n
                written = True
            elif code in self.CH_SUSPEND_ERRORS:
                self.logger.info("[%s] Timed out: %s", channel.name, body)
                metrics["error", ("type", "records_spool_timeouts")] += 1
                suspended = True
            else:
                self.logger.info("[%s] Failed to write records: %s %s", channel.name, code, body)
                metrics["error", ("type", "records_spool_failed")] += 1
        except Exception as e:
            self.logger.error(
                "[%s] Failed to spool %d records due to unknown error: %s", channel.name, n, e
            )
        channel.stop_flushing()
        if not written:
            # Return data back to channel
            channel.feed(data)
            if suspended:
                self.suspend()
            else:
                self.requeue_channel(channel)

    def requeue_channel(self, channel):
        channel.start_flushing()
        data = channel.get_data().splitlines()
        if not data:
            channel.stop_flushing()
            return
        self.logger.info("Requeueing %d records to topic %s", len(data), config.chwriter.topic)
        while data:
            chunk, data = data[: config.nsqd.ch_chunk_size], data[config.nsqd.ch_chunk_size :]
            cl = len(chunk)
            self.pub(config.chwriter.topic, "%s\n%s\n" % (channel.name, "\n".join(chunk)), raw=True)
            metrics["records_requeued"] += cl
            metrics["records_buffered"] -= cl
        channel.stop_flushing()

    def suspend(self):
        if self.restore_timeout:
            return
        self.logger.info("Suspending")
        self.restore_timeout = self.ioloop.add_timeout(
            self.ioloop.time() + float(config.chwriter.suspend_timeout_ms) / 1000.0,
            self.check_restore,
        )
        metrics["suspends"] += 1
        self.suspend_subscription(self.on_data)
        # Return data to channels
        self.requeue_channels()

    def requeue_channels(self):
        """
        Return buffered data back to queue
        :return:
        """
        for c in list(self.channels):
            channel = self.channels.get(c)
            self.requeue_channel(channel)

    def resume(self):
        if self.stopping:
            self.logger.info("Trying to restore during stopping. Ignoring")
            return
        self.logger.info("Resuming")
        self.ioloop.remove_timeout(self.restore_timeout)
        self.restore_timeout = None
        metrics["resumes"] += 1
        self.resume_subscription(self.on_data)

    @tornado.gen.coroutine
    def check_restore(self):
        if self.stopping:
            self.logger.info("Checking restore during stopping. Ignoring")
        else:
            code, headers, body = yield fetch(
                "http://%s/?user=%s&password=%s&database=%s&query=%s"
                % (
                    self.ch_address,
                    config.clickhouse.rw_user,
                    config.clickhouse.rw_password,
                    config.clickhouse.db,
                    "SELECT%20dummy%20FROM%20system.one",
                )
            )
            if code == 200:
                self.resume()
            else:
                self.restore_timeout = self.ioloop.add_timeout(
                    self.ioloop.time() + float(config.chwriter.suspend_timeout_ms) / 1000.0,
                    self.check_restore,
                )

    def stop(self):
        self.stopping = True
        # Stop consuming messages
        self.suspend_subscription(self.on_data)
        # Return messages back to queue
        self.requeue_channels()
        # .stop() will wait until queued data will be really published
        super(CHWriterService, self).stop()


if __name__ == "__main__":
    CHWriterService().start()
