## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-pmwriter daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
import logging
## NOC modules
from noc.lib.daemon import Daemon
from noc.lib.stomp.threadclient import ThreadedSTOMPClient
from noc.pm.models.storage import PMStorage
from noc.pm.models.ts import PMTS
from noc.pm.models.probe import PMProbe
from noc.pm.models.check import PMCheck


MAX32 = 0xFFFFFFFFL
MAX64 = 0xFFFFFFFFFFFFFFFFL


class PMWriterDaemon(Daemon):
    daemon_name = "noc-pmwriter"

    def __init__(self, *args, **kwargs):
        self.stomp_client = None
        self.storages = {}
        self.ts = {}  # ts_id -> PMTS
        # Last measures for COUNTER and DERIVE types
        self.last_measure = {}  # ts_id -> (timestamp, value)
        super(PMWriterDaemon, self).__init__(*args, **kwargs)

    def load_config(self):
        super(PMWriterDaemon, self).load_config()
        self.stomp_host = self.config.get("stomp", "host")
        self.stomp_port = self.config.getint("stomp", "port")
        self.stomp_client_id = self.config.get("stomp", "client_id")
        self.stomp_login = self.config.get("stomp", "login")
        self.stomp_password = self.config.get("stomp", "password")
        self.load_storages()

    def load_storages(self):
        for s in PMStorage.objects.all():
            if s.id not in self.storages:
                self.storages[s.id] = s

    def run(self):
        self.stomp_client = ThreadedSTOMPClient(
            host=self.stomp_host,
            port=self.stomp_port,
            login=self.stomp_login,
            passcode=self.stomp_password,
            client_id=self.stomp_client_id
        )
        self.stomp_client.start()
        self.stomp_client.subscribe("/queue/pm/data/", self.on_data)
        self.stomp_client.subscribe("/queue/pm/config/", self.on_config)
        self.stomp_client.wait()

    def on_data(self, destination, body):
        """
        Write timeseries data.
        Accepts list of (ts id, timestamp, value)
        :param destination:
        :param body:
        :return:
        """
        # Split data to storages
        spool = defaultdict(list)
        for ts_id, timestamp, value in body:
            ts = self.ts.get(ts_id)
            if ts is None:
                logging.error("Unknown time series id %s" % ts_id)
            else:
                # Check time series is enabled
                if not ts.is_active:
                    logging.debug("Ignore inactive time series %s" % ts)
                    continue  # Ignore inactive time series
                # Convert value
                if ts.type == "C":
                    value = self.convert_counter(ts, timestamp, value)
                elif ts.type == "D":
                    value = self.convert_derive(ts, timestamp, value)
                if value is None:
                    continue  # Skip round
                # Spool data for bulk save
                spool[ts.storage.id] += [(ts_id, timestamp, value)]
        # Write data
        for storage_id in spool:
            self.storages[storage_id].register(spool[storage_id])

    def on_config(self, destination, body):
        probe_name = body["probe"]
        probe = PMProbe.objects.filter(
            name=probe_name, is_active=True).first()
        if not probe:
            logging.error("Invalid probe: '%s'" % probe_name)
            return
        cfg = []
        for check in PMCheck.objects.filter(probe=probe):
            c = {
                "id": str(check.id),
                "check": check.check,
                "interval": check.interval,
                "config": check.config,
                "ts": {}
            }
            for ts in PMTS.objects.filter(check=check):
                self.ts[ts.id] = ts
                c["ts"][ts.name] = ts.id
            cfg += [c]
        self.stomp_client.send(cfg, "/queue/pm/config/%s/" % probe_name)

    def get_last_measure(self, ts):
        if ts.id not in self.last_measure:
            # Not in cache, fetch from database
            last_timestamp, last_value = ts.last_measure
            self.last_measure[ts.id] = (last_timestamp, last_value)
        return self.last_measure[ts.id]

    def convert_counter(self, ts, timestamp, value):
        last_timestamp, last_value = self.get_last_measure(ts)
        # Update last measure
        self.last_measure[ts.id] = (timestamp, value)
        if last_timestamp is None:
            # No data yet, save last measure and skip the round
            return None
        else:
            if value < last_value:
                # Counter wrapping adjustment
                mc = MAX64 if last_value >= MAX32 else MAX32
                last_value -= mc
            return (value - last_value) / (timestamp - last_timestamp)

    def convert_derive(self, ts, timestamp, value):
        last_timestamp, last_value = self.get_last_measure(ts)
        # Update last measure
        self.last_measure[ts.id] = (timestamp, value)
        if last_timestamp is None:
            # No data yet, save last measure and skip the round
            return None
        else:
            return (value - last_value) / (timestamp - last_timestamp)
