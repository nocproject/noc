# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Configuration thread
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import threading
import urllib2
import base64
import time
import logging
import datetime
## NOC modules
from noc.lib.serialize import json_decode
from noc.lib.debug import error_report


class ConfigurationThread(threading.Thread):
    def __init__(self, daemon):
        super(ConfigurationThread, self).__init__(name="configuration")
        self.daemon = daemon
        self.name = None
        self.url = None
        self.auth = None
        self.conf_lock = threading.Lock()
        self.last = None
        self.interval = None
        self.failed_interval = None
        self.timeout = None
        self.to_shutdown = None
        self.configs = {}  # uuid -> config
        self.changes = {}  # uuid -> change

    def info(self, msg):
        logging.info(msg)

    def debug(self, msg):
        logging.debug(msg)

    def error(self, msg):
        logging.debug(msg)

    def shutdown(self):
        self.to_shutdown = None

    def configure(self, name, url, user=None, passwd=None,
                  timeout=60, interval=60, failed_interval=10):
        self.debug("Configuring name=%s url=%s user=%s" % (name, url, user))
        with self.conf_lock:
            self.name = name
            if url.endswith("/"):
                url = url[:-1]
            self.url = "%s%s%s/%s/config/" % (
                url, self.daemon.AUTOCONF_PATH, self.name,
                self.daemon.instance_id
            )
            if user and passwd:
                self.auth = "Basic %s" % base64.encodestring(
                    "%s:%s" % (user, passwd)
                ).replace("\n", "")
            else:
                self.auth = None
            self.user = user
            self.passwd = passwd
            self.timeout = timeout
            self.interval = interval
            self.failed_interval = failed_interval

    def get_config(self):
        """
        Fetch config
        Returns dict or None
        """
        self.debug("Getting config")
        with self.conf_lock:
            url = self.url
        if self.last:
            url += "?last=%s" % self.last
        req = urllib2.Request(url)
        if self.auth:
            req.add_header("Authorization", self.auth)
        try:
            resp = urllib2.urlopen(req, timeout=self.timeout)
        except urllib2.URLError, why:
            self.error("Cannot get config from %s: %s" % (
                self.url, why))
            return None
        try:
            data = json_decode(resp.read())
        except:
            self.error("Failed to parse config")
            return None
        self.debug("Config retrieved")
        return data

    def apply_config(self, config):
        for cfg in config["config"]:
            try:
                u_id = cfg["uuid"]
                changed = cfg.pop("changed")
                expire = cfg.pop("expire")
            except KeyError, v:
                self.error("Configuration error: '%s' is missed" % v)
                continue
            if u_id not in self.configs:
                # Create new object
                self.configs[u_id] = cfg
                self.changes[u_id] = changed
                self.debug("Creating object %s: %s" % (u_id, cfg))
                self.daemon.on_object_create(**cfg)
            elif changed == expire:
                # Object deleted
                self.debug("Deleting object %s" % u_id)
                self.daemon.on_object_delete(u_id)
                del self.configs[u_id]
                del self.changes[u_id]
            elif self.changes[u_id] != changed:
                # Object changed
                self.configs[u_id] = cfg
                self.changes[u_id] = changed
                self.debug("Changing object %s: %s" % (u_id, cfg))
                self.daemon.on_object_change(**cfg)
        # Update last value
        self.last = config.get("now", datetime.datetime.now().isoformat())

    def run(self):
        self.info("Starting configuration thread")
        while not self.to_shutdown:
            try:
                t0 = time.time()
                interval = self.interval
                config = self.get_config()
                if config:
                    self.apply_config(config)
                elif config is None:
                    interval = self.failed_interval
                t = time.time()
                nt = t0 + interval
                if nt > t:
                    time.sleep(nt - t)
            except:
                error_report()
        self.info("Configuration thread stopped")
