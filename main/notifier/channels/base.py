# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NotificationChannel base class
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import inspect
import os
## NOC modules
from noc.lib.debug import error_report


class NotificationChannel(object):
    """
    Notification channel interface

    Configuration:
    [name]
    enabled = true | false
    instances = <N>
    """
    name = None

    def __init__(self, daemon, instance, queue):
        self.daemon = daemon
        self.instance = instance
        self.queue = queue
        self.to_shutdown = False
        self.display_label = "%s:%s" % (self.name, self.instance)

    @property
    def config(self):
        return self.daemon.config

    def run(self):
        self.info("Running")
        self.on_start()
        while not self.to_shutdown:
            id, to, subject, body, link = self.queue.get(block=True)
            try:
                r = self.send(to, subject, body, link)
                self.daemon.report_result(id, r)
            except Exception:
                error_report()
                self.daemon.report_result(id, False)
        self.on_shutdown()

    def debug(self, msg):
        logging.debug("[%s] %s" % (self.display_label, msg))

    def error(self, msg):
        logging.error("[%s] %s" % (self.display_label, msg))

    def info(self, msg):
        logging.info("[%s] %s" % (self.display_label, msg))

    def shutdown(self):
        self.to_shutdown = True

    def on_start(self):
        pass

    def on_shutdown(self):
        pass

    def send(self, to, subject, body, link=None):
        return False


class NotificationChannelRegistry(dict):
    def register_all(self):
        for f in os.listdir("main/notifier/channels"):
            if not f.endswith(".py") or f == "base.py":
                continue
            mn = "noc.main.notifier.channels.%s" % f[:-3]
            m = __import__(mn, {}, {}, "*")
            for on in dir(m):
                o = getattr(m, on)
                if (inspect.isclass(o) and
                        issubclass(o, NotificationChannel) and
                        o.__module__.startswith(mn)):
                    assert o.name
                    self[o.name] = o

notification_registry = NotificationChannelRegistry()
notification_registry.register_all()
