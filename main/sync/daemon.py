# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-sync daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
## NOC modules
from noc.lib.solutions import get_solution
from noc.lib.daemon.autoconf import AutoConfDaemon
from noc.sa.interfaces.base import DictParameter, InterfaceTypeError


class SyncDaemon(AutoConfDaemon):
    daemon_name = "noc-sync"
    AUTOCONF_PATH = "/main/sync/"

    def __init__(self):
        self.handlers = {}  # name -> handler
        self.tmap = {}  # type -> handler
        self.configured = set()  # set of handlers
        super(SyncDaemon, self).__init__()

    def load_config(self):
        super(SyncDaemon, self).load_config()
        left = set(self.handlers)
        for c in self.config.sections():
            if (c.startswith("sync:") and
                    self.config.has_option(c, "enabled") and
                    self.config.getboolean(c, "enabled")
            ):
                if c in self.handlers:
                    left.remove(c)
                    self.configure_handler(c)
                else:
                    self.add_handler(c)
        for c in left:
            self.close_handler(c)

    def close_handler(self, name):
        self.logger.info("Closing handler %s", name)
        self.handlers[name].close()
        del self.tmap[self.handlers[name].type]
        del self.handlers[name]

    def add_handler(self, name):
        self.logger.info("Initializing handler %s", name)
        h = self.config.get(name, "handler")
        hcls = get_solution(h)
        handler = hcls(self, name)
        self.handlers[name] = handler
        self.tmap[handler.type] = handler
        try:
            cfg = self.clean_config(handler)
        except InterfaceTypeError, why:
            self.logger.error("Cannot configure handler %s: %s",
                              name, why)
            self.close_handler(name)
            return
        self.logger.info("Configuring handler %s (%s): %s",
                         name, handler.type, cfg)
        try:
            handler.configure(**cfg)
        except ValueError, why:
            self.logger.error("Cannot configure handler %s: %s",
                              name, why)
            self.close_handler(name)

    def clean_config(self, handler):
        v = {}
        if isinstance(handler.config, dict):
            ci = DictParameter(attrs=handler.config)
        else:
            ci = handler.config
        # Read config
        for opt in self.config.options(handler.name):
            if opt not in ("enabled", "handler"):
                v[opt] = self.config.get(handler.name, opt)
        # Clean config
        return ci.clean(v)

    def run(self):
        while True:
            time.sleep(3)

    def on_object_create(self, uuid, **kwargs):
        type = kwargs.get("type")
        if not type:
            return
        handler = self.tmap.get(type)
        if not handler:
            self.logger.info("No handler for type %s, skipping", type)
            return
        handler.on_create(uuid, kwargs.get("data", {}))
        self.configured.add(handler)

    def on_object_delete(self, uuid):
        pass

    def on_object_change(self, uuid, **kwargs):
        type = kwargs.get("type")
        if not type:
            return
        handler = self.tmap.get(type)
        if not handler:
            self.logger.info("No handler for type %s, skipping", type)
            return
        handler.on_change(uuid, kwargs.get("data", {}))
        self.configured.add(handler)

    def on_configuration_done(self):
        """
        End of configuration round
        """
        for h in self.configured:
            h.on_configuration_done()
        self.configured = set()
