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


class PMWriterDaemon(Daemon):
    daemon_name = "noc-pmwriter"

    def __init__(self, *args, **kwargs):
        self.stomp_client = None
        self.storages = {}
        self.ts = {}  # ts_id -> PMTS
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
            if ts is not None:
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
