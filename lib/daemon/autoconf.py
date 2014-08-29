# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Autoconfigurated daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import Daemon
from configuration import ConfigurationThread


class AutoConfDaemon(Daemon):
    # Relative path to autoconf service
    AUTOCONF_PATH = None

    def __init__(self):
        self.configuration_thread = None
        super(AutoConfDaemon, self).__init__()

    def load_config(self):
        super(AutoConfDaemon, self).load_config()
        # Run configuraton thread
        to_start = not bool(self.configuration_thread)
        if not self.configuration_thread:
            self.configuration_thread = ConfigurationThread(self)
        self.configuration_thread.configure(
            name=self.config.get("autoconf", "name"),
            url=self.config.get("autoconf", "url"),
            user=self.config.get("autoconf", "user") or None,
            passwd=self.config.get("autoconf", "passwd") or None,
            interval=self.config.getint("autoconf", "interval"),
            failed_interval=self.config.getint("autoconf", "failed_interval"),
            timeout=self.config.getint("autoconf", "timeout")
        )
        if to_start:
            self.configuration_thread.start()

    def on_object_create(self, uuid, **kwargs):
        pass

    def on_object_delete(self, uuid):
        pass

    def on_object_change(self, uuid, **kwargs):
        pass