# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import os
from threading import Lock
import re
## Third-party modules
import six
import ujson
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmetrics import IGetMetrics
from noc.lib.mib import mib
from noc.core.handler import get_handler

NS = 1000000000.0

OID_GENERATOR_TYPE = {}

rx_rule_var = re.compile(r"{{\s*([^}]+?)\s*}}")


class OIDRuleBase(type):
    def __new__(mcs, name, bases, attrs):
        m = type.__new__(mcs, name, bases, attrs)
        OID_GENERATOR_TYPE[m.name] = m
        return m


@six.add_metaclass(OIDRuleBase)
class OIDRule(object):
    """
    SNMP OID generator for SNMP_OIDS
    """
    name = "oid"
    default_type = "gauge"

    def __init__(self, oid, type=None, scale=1):
        self.oid = oid
        self.is_complex = not isinstance(oid, six.string_types)
        self.type = type or self.default_type
        if isinstance(scale, six.string_types):
            self.scale = get_handler(
                "noc.core.script.metrics.%s" % scale
            )
        else:
            self.scale = scale

    def iter_oids(self, script, metric):
        """
        Generator yielding oid, type, scale, tags
        :param script:
        :param metric:
        :return:
        """
        if self.is_complex:
            yield tuple(self.oid), self.type, self.scale, {}
        else:
            yield self.oid, self.type, self.scale, {}

    @classmethod
    def load(cls, data):
        """
        Create from data structure
        :param data:
        :return:
        """
        if type(data) != dict:
            raise ValueError("object required")
        if "$type" not in data:
            raise ValueError("$type key is required")
        t = data["$type"]
        if t not in OID_GENERATOR_TYPE:
            raise ValueError("Invalid $type '%s'" % t)
        return OID_GENERATOR_TYPE[t].from_json(data)

    @classmethod
    def from_json(cls, data):
        kwargs = {}
        for k in data:
            if not k.startswith("$"):
                kwargs[k] = data[k]
        return cls(**kwargs)

    @classmethod
    def expand(cls, template, context):
        """
        Expand {{ var }} expressions in template with given context
        :param template:
        :param context:
        :return:
        """
        return rx_rule_var.sub(
            lambda x: str(context[x.group(1)]),
            template
        )


class CounterRule(OIDRule):
    """
    SNMP OID for SNMP counters
    """
    name = "counter"
    default_type = "counter"


class BooleanRule(OIDRule):
    """
    SNMP OID for booleans
    """
    name = "bool"
    default_type = "bool"


@six.add_metaclass(OIDRuleBase)
class CapabilityRule(object):
    """
    Capability-based selection

    oids is the list of (Capability, OIDRule)
    """
    name = "caps"

    def __init__(self, oids):
        self.oids = oids

    def iter_oids(self, script, metric):
        for cap, oid in self.oids:
            if script.has_capability(cap):
                for r in oid.iter_oids(script, metric):
                    yield r
                break

    @classmethod
    def from_json(cls, data):
        if "oids" not in data:
            raise ValueError("oids is required")
        if type(data["oids"]) != list:
            raise ValueError("oids must be list")
        return CapabilityRule(
            oids=[OIDRule.load(d) for d in data["oids"]]
        )


@six.add_metaclass(OIDRuleBase)
class HiresRule(object):
    """
    Select *hires* chain if SNMP | IF-MIB HC capability set,
    Select *normal* capability otherwise
    """
    name = "hires"

    def __init__(self, hires, normal):
        self.hires = hires
        self.normal = normal

    def iter_oids(self, script, metric):
        if script.has_capability("SNMP | IF-MIB | HC"):
            g = self.hires.iter_oids
        else:
            g = self.normal.iter_oits
        for r in g(script, metric):
            yield r

    @classmethod
    def from_json(cls, data):
        for v in ("hires", "normal"):
            if v not in data:
                raise ValueError("%s is required" % v)
        return HiresRule(
            hires=OIDRule.load(data["hires"]),
            normal=OIDRule.load(data["normal"])
        )


class InterfaceRule(OIDRule):
    """
    Expand %(ifIndex)s
    """
    name = "ifindex"

    def iter_oids(self, script, metric):
        for i in metric["interfaces"]:
            ifindex = script.get_ifindex(i)
            if ifindex:
                if self.is_complex:
                    # oid is list
                    for o in self.oid:
                        oid = mib[self.expand(o, {"ifIndex": ifindex})]
                        if oid:
                            yield oid, self.type, self.scale, {"interface": i}
                else:
                    oid = mib[self.expand(self.oid, {"ifIndex": ifindex})]
                    if oid:
                        yield oid, self.type, self.scale, {"interface": i}


class Script(BaseScript):
    """
    Retrieve data for topology discovery
    """
    name = "Generic.get_metrics"
    interface = IGetMetrics
    requires = []

    # Aggregate up to GET_CHUNK requests
    GET_CHUNK = 15
    # Define counter types
    GAUGE = "gauge"
    COUNTER = "counter"
    #
    _SNMP_OID_RULES = {}  # Profile -> metric type ->
    _SNMP_OID_LOCK = Lock()

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
        if self.has_capability("SNMP"):
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
        Collect all collectible SNMP metrics
        """
        batch = {}
        for m in metrics:
            # Calculate oids
            snmp_rule = self.get_snmp_rule(m)
            if snmp_rule:
                for oid, vtype, scale, tags in snmp_rule.iter_oids(self, metrics[m]):
                    batch[oid] = {
                        "name": m,
                        "tags": tags,
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

    def get_snmp_rule(self, metric_type):
        profile = self.profile.name
        if profile not in self._SNMP_OID_RULES:
            self.load_snmp_rules(profile)
        return self._SNMP_OID_RULES[profile].get(metric_type)

    @classmethod
    def load_snmp_rules(cls, profile):
        """
        Initialize SNMP rules from JSON
        :param profile:
        :return:
        """
        with cls._SNMP_OID_LOCK:
            if profile in cls._SNMP_OID_RULES:
                # Load by concurrent thread
                return
            cls._SNMP_OID_RULES[profile] = {}
            v, p = profile.split(".")
            for path in [
                os.path.join("sa", "profiles", "Generic", "snmp_metrics"),
                os.path.join("sa", "profiles", v, p, "snmp_metrics"),
                os.path.join("custom", "sa", "profiles", "Generic", "snmp_metrics"),
                os.path.join("custom", "sa", v, p, "snmp_metrics")
            ]:
                cls.apply_rules_from_dir(
                    cls._SNMP_OID_RULES[profile],
                    path
                )

    @classmethod
    def apply_rules_from_dir(cls, rules, path):
        if not os.path.exists(path):
            return
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".json"):
                    cls.apply_rules_from_json(rules,
                                              os.path.join(root, f))

    @classmethod
    def apply_rules_from_json(cls, rules, path):
        # @todo: Check read access
        with open(path) as f:
            data = f.read()
        try:
            data = ujson.loads(data)
        except ValueError as e:
            raise ValueError(
                "Failed to parse file '%s': %s" % (path, e)
            )
        if type(data) != dict:
            raise ValueError(
                "Error in file '%s': Must be defined as object" % path
            )
        if "$metric" not in data:
            raise ValueError("$metric key is required")
        rules[data["$metric"]] = OIDRule.load(data)
