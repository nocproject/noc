#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import threading
# Third-party modules
import tornado.ioloop
import tornado.gen
import tornado.httpclient
## NOC modules
from noc.core.service.base import Service
from noc.core.scheduler.scheduler import Scheduler


class DiscoveryService(Service):
    name = "discovery"
    leader_group_name = "discovery-%(pool)s"
    pooled = True
    process_name = "noc-%(name).10s-%(instance).2s-%(pool).3s"

    def __init__(self):
        super(DiscoveryService, self).__init__()
        self.scheduler = None
        self.metrics = []
        self.metrics_lock = threading.Lock()
        self.send_callback = None

    @tornado.gen.coroutine
    def on_activate(self):
        # Send spooled messages every 250ms
        self.logger.debug("Stating message sender task")
        self.send_callback = tornado.ioloop.PeriodicCallback(
            self.send_metrics,
            250,
            self.ioloop
        )
        self.send_callback.start()
        if self.config.global_n_instances > 1:
            ifilter = {
                "key": {
                    "$mod": [
                        self.config.global_n_instances,
                        self.config.instance + self.config.global_offset
                    ]
                }
            }
        else:
            ifilter = None
        self.scheduler = Scheduler(
            "discovery",
            pool=self.config.pool,
            reset_running=True,
            max_threads=self.config.max_threads,
            ioloop=self.ioloop,
            filter=ifilter
        )
        self.scheduler.service = self
        self.scheduler.run()

    @tornado.gen.coroutine
    def send_metrics(self):
        """
        Send collected metrics to InfluxDB
        """
        with self.metrics_lock:
            if not self.metrics:
                return
            msg = "\n".join(self.metrics)
            self.metrics = []
        # Send collected metrics
        for s in self.resolve_service("influxdb"):
            client = tornado.httpclient.AsyncHTTPClient(
                force_instance=True,
                max_clients=1
            )
            try:
                response = yield client.fetch(
                    # @todo: Configurable database name
                    "http://%s/write?db=noc&precision=s" % s,
                    method="POST",
                    body=msg
                )
                # @todo: Check for 204
                msg = ""
            except tornado.httpclient.HTTPError as e:
                self.logger.error(
                    "Failed to spool collected metrics to %s: %s",
                    s, str(e)
                )
            except Exception as e:
                self.logger.error(
                    "Failed to spool collected metrics to %s: %s",
                    s, str(e)
                )
            finally:
                client.close()
                # Resolve CurlHTTPClient circular dependencies
                client._force_timeout_callback = None
                client._multi = None
        if msg:
            # Return metrics to queue
            with self.metrics_lock:
                self.metrics = [msg] + self.metrics

    def register_metrics(self, batch):
        with self.metrics_lock:
            self.metrics += [batch]


if __name__ == "__main__":
    DiscoveryService().start()
