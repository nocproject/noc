# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FM sender
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import threading
import logging
import time
import urllib2
import socket
## NOC modules
from noc.lib.debug import error_report
from noc.lib.serialize import json_encode

logger = logging.getLogger(__name__)


class FMSender(threading.Thread):
    def __init__(self, daemon):
        self._daemon = daemon
        self.data = None
        self.clear_data()
        self.data_lock = threading.Lock()
        self.data_event = threading.Event()
        super(FMSender, self).__init__(name="fmsender")

    def clear_data(self):
        self.data = {
            "thresholds": []
        }

    def run(self):
        logger.info("Running FM sender")
        while True:
            self.data_event.wait()
            with self.data_lock:
                data = self.data
                self.clear_data()
                self.data_event.clear()
            try:
                if not self.send_data(data):
                    self.restore_data(data)
            except:
                error_report()
                self.restore_data(data)
            time.sleep(1)  # Prevent CPU hogging

    def feed_threshold(self, managed_object, metric, metric_type, t, v,
                       old_state, new_state):
        with self.data_lock:
            self.data["thresholds"] += [{
                "managed_object": managed_object,
                "metric": metric,
                "metric_type": metric_type,
                "ts": t,
                "value": v,
                "old_state": old_state,
                "new_state": new_state
            }]
            self.data_event.set()

    def send_data(self, data):
        logger.debug("Sending data")
        conf = self._daemon.configuration_thread
        with conf.conf_lock:
            url = conf.url[:-8] + "/feed/"
            auth = conf.auth
        timeout = 60
        req = urllib2.Request(url)
        if auth:
            req.add_header("Authorization", auth)
        req.add_header("Content-Type", "text/json")
        req.add_data(json_encode(data))
        try:
            urllib2.urlopen(req, timeout=timeout)
        except urllib2.URLError, why:
            logger.error("Cannot feed data to %s: %s",
                         url, why)
            return False
        except socket.timeout:
            logger.error("Cannot feed data to %s: Timed out",
                         url)
            return False
        except socket.error, why:
            logger.error("Cannot feed data to %s: Socket error: %s",
                         url, why)
            return False
        return True

    def restore_data(self, data):
        """
        Return data to sending queue
        """
        logger.info("Restoring stale data")
        with self.data_lock:
            self.data["thresholds"] = data["thresholds"] + self.data["thresholds"]
