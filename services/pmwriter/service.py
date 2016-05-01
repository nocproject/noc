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

    def __init__(self):
        super(PMWriterService, self).__init__()
        self.queue = None
        self.influx = None

    @tornado.gen.coroutine
    def on_activate(self):
        self.queue = tornado.queues.Queue(maxsize=self.config.batch_size)
        self.influx = self.resolve_service("influxdb", 1)[0]
        self.subscribe(
            "metrics",
            "pmwriter",
            self.on_metric,
            max_in_flight=self.config.batch_size * 2
        )

    def on_metric(self, message, metric, *args, **kwargs):
        """
        Called on new dispose message
        """
        self.queue.put(metric)
        return True

    @tornado.gen.coroutine
    def send_metrics(self):
        while True:
            batch = []
            # Wait for first metric
            m = yield self.queue.get()
            batch += [m]
            # Populate batch up to recommented size
            while len(batch) < self.config.batch_size:
                try:
                    m = yield self.queue.get_nowait()
                    batch += [m]
                except tornado.queues.QueueEmpty:
                    break
            body = "\n".join(batch)
            while True:
                t0 = time.time()
                self.logger.debug("Sending %d metrics", len(batch))
                client = tornado.httpclient.AsyncHTTPClient()
                try:
                    response = client.fetch(
                        # Configurable database name
                        "http://%s/write?db=noc&precision=s" % self.influx,
                        method="POST",
                        body=body
                    )
                    # @todo: Check for 204
                    self.logger.info(
                        "%d metrics sent in %.2fms",
                        len(batch), (time.time() - t0) * 1000
                    )
                    break
                except tornado.httpclient.HTTPError as e:
                    self.logger.error("Failed to spool %d metrics: %s",
                                      len(batch), e)
                except Exception as e:
                    self.logger.error(
                        "Failed to spool %d metrics due to unknown error: %s",
                        len(batch), e
                    )


if __name__ == "__main__":
    PMWriterService().start()
