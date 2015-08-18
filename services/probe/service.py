#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Probe service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
from optparse import make_option
import datetime
# Third-party modules
import tornado.ioloop
import tornado.gen
## NOC modules
from noc.lib.service.base import Service
from noc.sa.interfaces.base import StringParameter


class ProbeService(Service):
    name = "probe"

    pooled = True
    # Dict parameter containing values accepted
    # via dynamic configuration
    config_interface = {
        "loglevel": StringParameter(
            default=os.environ.get("NOC_LOGLEVEL", "info"),
            choices=["critical", "error", "warning", "info", "debug"]
        )
    }

    service_option_list = [
        make_option(
            "-l", "--listen",
            action="append", dest="listen",
            default=[os.environ.get("NOC_LISTEN", "0.0.0.0:514")],
            help="Listen addresses"
        )
    ]

    def __init__(self):
        super(ProbeService, self).__init__()
        self.probeconf = None
        self.pmwriter = None
        self.get_config_callback = None
        self.send_metrics_callback = None
        self.last_update = None
        self.metrics = []
        self.configs = {}  # uuid -> config
        self.changes = {}  # uuid -> change

    def on_activate(self):
        # Register RPC aliases
        self.probeconf = self.open_rpc_pool("probeconf")
        self.pmwriter = self.open_rpc_global("pmwriter")
        # Get probe config every 60s
        self.logger.debug("Stating configuration task")
        self.get_config_callback = tornado.ioloop.PeriodicCallback(
            self.get_probe_config,
            60000,
            self.ioloop
        )
        self.get_config_callback.start()
        self.ioloop.add_callback(self.get_probe_config)
        # Send metrics every 250ms
        self.logger.debug("Stating sender task")
        self.send_metrics_callback = tornado.ioloop.PeriodicCallback(
            self.send_metrics,
            250,
            self.ioloop
        )
        self.send_metrics_callback.start()

    @tornado.gen.coroutine
    def send_metrics(self):
        """
        Periodic task to send metrics
        """
        if self.metrics:
            yield self.pmwriter.metrics(self.metrics, _async=True)
            self.metrics = []

    @tornado.gen.coroutine
    def get_probe_config(self):
        self.logger.debug("Get probe config")
        config = yield self.probeconf.get_config(self.last_update)
        self.apply_config(config)
        self.last_update = config.get(
            "now",
            datetime.datetime.now().isoformat()
        )

    def apply_config(self, config):
        n = 0
        n_new = 0
        n_changed = 0
        n_errors = 0
        n_deleted = 0
        for cfg in config["config"]:
            n += 1
            try:
                u_id = cfg["uuid"]
                changed = cfg.pop("changed")
                expire = cfg.pop("expire")
            except KeyError, v:
                self.logger.error("Configuration error: '%s' is missed" % v)
                n_errors += 1
                continue
            if u_id not in self.configs:
                # Create new object
                self.configs[u_id] = cfg
                self.changes[u_id] = changed
                self.logger.debug("Creating object %s: %s" % (u_id, cfg))
                self.create_probe(**cfg)
                n_new += 1
            elif changed == expire:
                # Object deleted
                self.logger.debug("Deleting object %s" % u_id)
                self.delete_probe(u_id)
                del self.configs[u_id]
                del self.changes[u_id]
                n_deleted += 1
            elif self.changes[u_id] != changed:
                # Object changed
                self.configs[u_id] = cfg
                self.changes[u_id] = changed
                self.logger.debug("Changing object %s: %s" % (u_id, cfg))
                self.change_probe(**cfg)
                n_changed += 1
        # Update last value
        self.logger.debug(
            "Configuration has been applied: "
            "Items: %d, New: %d, Changed: %d, Deleted: %d, Errors: %d",
            n, n_new, n_changed, n_deleted, n_errors
        )

    def create_probe(self, **kwargs):
        pass

    def delete_probe(self, probe_id):
        pass

    def change_probe(self, **kwargs):
        pass

if __name__ == "__main__":
    ProbeService().start()
