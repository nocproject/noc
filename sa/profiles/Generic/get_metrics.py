# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
from collections import namedtuple
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmetrics import IGetMetrics
from noc.lib.mib import mib


class Script(BaseScript):
    """
    Retrieve data for topology discovery
    """
    name = "Generic.get_discovery_id"
    interface = IGetMetrics
    requires = []

    SNMP_OIDS = {
        "Interface | Load | In": [
            ("SNMP | IF-MIB | HC", "IF-MIB::ifHCInOctets"),
            ("SNMP | IF-MIB", "IF-MIB::ifInOctets")
        ],
        "Interface | Load | Out": [
            ("SNMP | IF-MIB | HC", "IF-MIB::ifHCOutOctets"),
            ("SNMP | IF-MIB", "IF-MIB::ifOutOctets")
        ]
    }

    def __init__(self, *args, **kwargs):
        super(Script, self).__init__(*args, **kwargs)
        self.metrics = []
        self.tags = {
            "object": self.credentials.get("name")
        }
        self.ifindexes = {}

    def execute(self, metrics, hints=None):
        # Populate ifindexes
        hints = hints or {}
        self.ifindexes = hints.get("ifindexes", {})
        #
        self.collect_profile_metrics()
        self.collect_snmp_metrics(metrics)
        #
        return self.get_metrics()

    def collect_profile_metrics(self, metrics):
        """
        Profile extension
        """
        pass

    def collect_snmp_metrics(self, metrics):
        """
        Collect all collectable SNMP metrics
        """
        for m in metrics:
            batch = {}
            # Calucate iods
            if m in self.SNMP_OIDS:
                if m["scope"] == "i":
                    for i in m["interfaces"]:
                        ifindex = self.get_ifindex(i)
                        if ifindex:
                            oid = self.resolve_oid(self.SNMP_OIDS[m], ifindex)
                            if oid:
                                batch[oid] = {
                                    "name": m,
                                    "tags": {
                                        "object": self.credentials.name,
                                    }
                                }
                else:
                    pass  # @todo: Spool object's metrics
            # Run snmp batch
            if batch:
                # @todo: Switch to bulk ops when necessary
                for oid in batch:
                    ts = self.get_ts()
                    v = self.snmp.get(oid)
                    if v is not None:
                        self.set_metric(
                            name=batch[oid]["name"],
                            value=v,
                            ts=ts,
                            tags=batch[oid]["tags"]
                        )

    def resolve_oid(self, chain, ifindex=None):
        """
        Return first suitable oid for OID_*, or None if not founc
        """
        for c, o in chain:
            if c in self.capabilities:
                if ifindex:
                    return mib[o, ifindex]
                else:
                    return mib[o]
        return None

    def get_ifindex(self, name):
        return self.ifindexes.get(name)

    @staticmethod
    def get_ts():
        """
        Returns current timestamp in nanoseconds
        """
        return int(time.time() * 1000000)

    def set_metric(self, name, value, ts=None, tags=None):
        """
        Append metric to output
        """
        tags = tags or {}
        tags = tags.copy()
        tags.update(self.tags)
        self.metrics += [{
            "ts": ts or self.get_ts(),
            "name": name,
            "value": value,
            "tags": tags
        }]

    def get_metrics(self):
        return self.metrics
