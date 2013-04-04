# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-sync daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import threading
## NOC modules
from noc.lib.daemon import Daemon
from noc.lib.stomp.threadclient import ThreadedSTOMPClient
from noc.lib.modutils import load_subclasses
from channel import Channel


class SyncDaemon(Daemon):
    daemon_name = "noc-sync"

    def __init__(self):
        self.channels = {}  # name -> Channel instance
        super(SyncDaemon, self).__init__()
        logging.info("Running noc-sync")

    def load_config(self):
        super(SyncDaemon, self).load_config()
        # STOMP settings
        self.stomp_host = self.config.get("stomp", "host")
        self.stomp_port = self.config.getint("stomp", "port")
        self.stomp_client_id = self.config.get("stomp", "client_id")
        self.stomp_login = self.config.get("stomp", "login")
        self.stomp_password = self.config.get("stomp", "password")
        # Load channels
        for ch in self.config.sections():
            if "/" not in ch:
                continue
            self.load_channel(ch)

    def load_channel(self, channel):
        if not self.config.getboolean(channel, "enabled"):
            logging.info("Skipping disabled channel %s" % channel)
            return
        parts = channel.split("/")
        ch_name = parts.pop(-1)
        c_type = self.config.get(channel, "type", None)
        if c_type:
            parts += c_type.split("/")
        mn = "noc.main.sync.channels.%s" % ".".join(parts)
        c = load_subclasses(mn, Channel)
        if not c or len(c) != 1:
            self.die("Unable to load channel %s" % channel)
        config = {}
        for opt in self.config.options(channel):
            config[opt] = self.config.get(channel, opt)
        self.channels[channel] = c[0](self, channel, ch_name, config)

    def run(self):
        self.stomp_client = ThreadedSTOMPClient(
            self.stomp_host, self.stomp_port,
            login=self.stomp_login,
            passcode=self.stomp_password,
            client_id=self.stomp_client_id)
        self.stomp_client.start()
        for c in self.channels:
            self.channels[c].init()
        while self.stomp_client.factory_thread.is_alive():
            self.stomp_client.factory_thread.join(1)

    def send(self, message, destination,
             receipt=False, persistent=False, expires=None):
        self.stomp_client.send(message, destination,
            receipt=receipt, persistent=persistent, expires=expires)

    def subscribe(self, destination, callback):
        self.stomp_client.subscribe(destination, callback)