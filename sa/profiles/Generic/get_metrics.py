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

NS = 1000000000.0


class Script(BaseScript):
    """
    Retrieve data for topology discovery
    """
    name = "Generic.get_metrics"
    interface = IGetMetrics
    requires = []

    # Dict of
    # metric type -> list of (capability, oid, type, scale)
    # To override use
    # SNMP_OIDS = BaseScript.merge_oids({
    # ...
    # })
    SNMP_OIDS = {
        "Interface | Load | In": [
            ("SNMP | IF-MIB | HC", "IF-MIB::ifHCInOctets", "counter", 8),
            ("SNMP | IF-MIB", "IF-MIB::ifInOctets", "counter", 8)
        ],
        "Interface | Load | Out": [
            ("SNMP | IF-MIB | HC", "IF-MIB::ifHCOutOctets", "counter", 8),
            ("SNMP | IF-MIB", "IF-MIB::ifOutOctets", "counter", 8)
        ],
        "Interface | Errors | In": [
            ("SNMP | IF-MIB", "IF-MIB::ifInErrors", "counter", 1)
        ],
        "Interface | Errors | Out": [
            ("SNMP | IF-MIB", "IF-MIB::ifOutErrors", "counter", 1)
        ],
        "Interface | Discards | In": [
            ("SNMP | IF-MIB", "IF-MIB::ifInDiscards", "counter", 1)
        ],
        "Interface | Discards | Out": [
            ("SNMP | IF-MIB", "IF-MIB::ifOutDiscards", "counter", 1)
        ],
        "Interface | Packets | In": [
            ("SNMP | IF-MIB | HC", "IF-MIB::ifHCInUcastPkts", "counter", 1),
            ("SNMP | IF-MIB", "IF-MIB::ifInUcastPkts", "counter", 1)
        ],
        "Interface | Packets | Out": [
            ("SNMP | IF-MIB | HC", "IF-MIB::ifHCOutUcastPkts", "counter", 1),
            ("SNMP | IF-MIB", "IF-MIB::ifOutUcastPkts", "counter", 1)
        ]
    }

    GAUGE = "gauge"
    COUNTER = "counter"

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
        self.collect_profile_metrics(metrics)
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
        batch = {}
        for m in metrics:
            # Calculate oids
            if m in self.SNMP_OIDS:
                if metrics[m]["scope"] == "i":
                    # Apply interface metrics
                    for i in metrics[m]["interfaces"]:
                        ifindex = self.get_ifindex(i)
                        if ifindex:
                            oid, vtype, scale = self.resolve_oid(self.SNMP_OIDS[m], ifindex)
                            if oid:
                                batch[oid] = {
                                    "name": m,
                                    "tags": {
                                        "interface": i
                                    },
                                    "type": vtype,
                                    "scale": scale
                                }
                else:
                    # Apply object metric
                    oid, vtype, scale = self.resolve_oid(self.SNMP_OIDS[m])
                    if oid:
                        batch[oid] = {
                            "name": m,
                            "tags": {},
                            "type": vtype,
                            "scale": scale
                        }
        # Run snmp batch
        if batch:
            # @todo: Switch to bulk ops when necessary
            for oid in batch:
                ts = self.get_ts()
                if isinstance(oid, basestring):
                    # Single oid
                    try:
                        v = self.snmp.get(oid)
                        if v is None:
                            continue
                    except self.snmp.TimeOutError as e:
                        self.logger.error(
                            "Failed to get SNMP OID %s: %s",
                            oid, e
                        )
                        continue
                elif callable(batch[oid]["scale"]):
                    # Multiple oids and calculated value
                    v = []
                    for o in oid:
                        try:
                            vv = self.snmp.get(oid)
                            v += [vv]
                            if vv is None:
                                break
                        except self.snmp.TimeOutError as e:
                            self.logger.error(
                                "Failed to get SNMP OID %s: %s",
                                o, e
                            )
                            v += [None]
                            break
                    # Check result does not contain None
                    if any(1 for vv in v if vv is None):
                        self.logger.error(
                            "Cannot calculate complex value for %s "
                            "due to missed values: %s",
                            oid, v
                        )
                        continue
                else:
                    self.logger.error(
                        "Cannot evaluate complex oid %s. "
                        "Scale must be callable",
                        oid
                    )
                    continue
                self.set_metric(
                    name=batch[oid]["name"],
                    value=v,
                    ts=ts,
                    tags=batch[oid]["tags"],
                    type=batch[oid]["type"],
                    scale=batch[oid]["scale"]
                )

    def resolve_oid(self, chain, ifindex=None):
        """
        Return first suitable oid for OID_*, or None if not founc
        """
        for cap, o, type, scale in chain:
            if cap in self.capabilities:
                if ifindex:
                    return mib[o, ifindex], type, scale
                else:
                    return mib[o], type, scale
        return None, None

    def get_ifindex(self, name):
        return self.ifindexes.get(name)

    @staticmethod
    def get_ts():
        """
        Returns current timestamp in nanoseconds
        """
        return int(time.time() * NS)

    def set_metric(self, name, value, ts=None, tags=None,
                   type="gauge", scale=1):
        """
        Append metric to output
        """
        tags = tags or {}
        tags = tags.copy()
        tags.update(self.tags)
        if callable(scale):
            if not isinstance(value, list):
                value = [value]
            value = scale(*value)
            scale = 1
        self.metrics += [{
            "ts": ts or self.get_ts(),
            "name": name,
            "value": value,
            "tags": tags,
            "type": type,
            "scale": scale
        }]

    def get_metrics(self):
        return self.metrics

    @classmethod
    def merge_oids(cls, oids):
        """
        Build summary oids for SNMP_OIDS
        """
        r = Script.SNMP_OIDS.copy()
        r.update(oids)
        return r
