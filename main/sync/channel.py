# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Sync channel
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import logging
import threading


class Channel(object):
    def __init__(self, daemon, channel, name, config):
        self.daemon = daemon
        self.channel = channel
        self.name = name
        self.root = "/queue/sync/%s/" % "/".join(self.channel.split("/")[:-1])
        self.lock = threading.Lock()

    def die(self, msg):
        self.daemon.die("[%s] %s" % (self.channel, msg))

    def info(self, msg):
        logging.info("[%s] %s" % (self.channel, msg))

    def error(self, msg):
        logging.error("Error: [%s] %s" % (self.channel, msg))

    def init(self):
        self.daemon.subscribe(self.root + self.name + "/",
            self.on_msg)
        self.list()

    def send(self, msg, destination):
        return self.daemon.send(msg, destination)

    def list(self):
        """
        Request LIST command
        :return:
        """
        self.send({
            "cmd": "list",
            "channel": self.name,
        }, self.root)

    def verify(self, objects):
        self.send({
            "cmd": "verify",
            "channel": self.name,
            "objects": list(objects)
        }, self.root)

    def on_msg(self, destination, msg):
        cmd = msg.get("cmd")
        if not cmd:
            return
        if cmd == "list":
            if "items" in msg:
                with self.lock:
                    self.on_list(msg["items"])
        elif cmd == "verify":
            if "object" in msg and "data" in msg:
                with self.lock:
                    self.on_verify(msg["object"], msg["data"])
        elif cmd == "request":
            if "request" in msg:
                if msg["request"] == "list":
                    self.list()
                elif msg["request"] == "verify" and "object" in msg:
                    self.verify([msg["object"]])

    def on_list(self, items):
        """
        :param items: Dict of name -> version
        :return:
        """
        pass

    def on_verify(self, object, data):
        pass
