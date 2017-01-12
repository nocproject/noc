# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
## Third-party modules
import six
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

    # Aggregate up to GET_CHUNK requests
    GET_CHUNK = 15

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
        ],
        "Interface | Status | Admin": [
            ("SNMP | IF-MIB", "IF-MIB::ifAdminStatus", "bool", lambda x: 1 if x == 1 else 0)
        ],
        "Interface | Status | Oper": [
            ("SNMP | IF-MIB", "IF-MIB::ifOperStatus", "bool", lambda x: 1 if x == 1 else 0)
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
        """
        metrics is the dict of
        name ->
            scope:
                o - object level
                i - interface level
                p - profile level
            interfaces: [list of interface names], for *i* scope
            probes: [{
                tests: [{
                    name
                    type
                }
            }] for *p* scope
        """
        # Populate ifindexes
        hints = hints or {}
        self.ifindexes = hints.get("ifindexes", {})
        self.probes = hints.get("probes", {})
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
        if not batch:
            self.logger.debug("Nothing to fetch via SNMP")
            return
        # Optimize fetching, aggregating up to GET_CHUNK
        # in single request
        oids = set()
        for o in batch:
            if isinstance(o, six.string_types):
                oids.add(o)
            else:
                oids.update(o)
        oids = list(oids)
        results = {}  # oid -> value
        while oids:
            chunk, oids = oids[:self.GET_CHUNK], oids[self.GET_CHUNK:]
            chunk = dict((x, x) for x in chunk)
            try:
                results.update(
                    self.snmp.get(chunk)
                )
            except self.snmp.TimeOutError as e:
                self.logger.error(
                    "Failed to get SNMP OIDs %s: %s",
                    oids, e
                )
        # Process results
        for oid in batch:
            ts = self.get_ts()
            if isinstance(oid, six.string_types):
                if oid in results:
                    v = results[oid]
                    if v is None:
                        continue
                else:
                    self.logger.error(
                        "Failed to get SNMP OID %s",
                        oid
                    )
                    continue
            elif callable(batch[oid]["scale"]):
                # Multiple oids and calculated value
                v = []
                for o in oid:
                    if o in results:
                        vv = results[o]
                        if vv is None:
                            break
                        else:
                            v += [vv]
                    else:
                        self.logger.error(
                            "Failed to get SNMP OID %s",
                            o
                        )
                        break
                # Check result does not contain None
                if len(v) < len(oid):
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
        def rmib(v):
            if isinstance(v, six.string_types):
                if ifindex:
                    return mib[v, ifindex]
                else:
                    return mib[v]
            else:
                return tuple(rmib(x) for x in v)

        for cap, o, type, scale in chain:
            if cap in self.capabilities:
                return rmib(o), type, scale
        return None, None, None

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
