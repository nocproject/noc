# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import os
from threading import Lock
import re
# Third-party modules
import six
import ujson
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmetrics import IGetMetrics
from noc.core.mib import mib
from noc.core.handler import get_handler
from noc.core.matcher import match

NS = 1000000000.0

OID_GENERATOR_TYPE = {}

rx_rule_var = re.compile(r"{{\s*([^}]+?)\s*}}")


class MetricConfig(object):
    __slots__ = (
        "id",
        "metric",
        "path",
        "ifindex",
        "sla_type"
    )

    def __init__(self, id, metric, path=None, ifindex=None,
                 sla_type=None):
        self.id = id
        self.metric = metric
        self.path = path
        self.ifindex = ifindex
        self.sla_type = sla_type

    def __repr__(self):
        return "<MetricConfig #%s %s>" % (self.id, self.metric)


class BatchConfig(object):
    __slots__ = ("id", "metric", "path", "type", "scale")

    def __init__(self, id, metric, path, type, scale):
        self.id = id
        self.metric = metric
        self.path = path
        self.type = type
        self.scale = scale


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

    def __init__(self, oid, type=None, scale=1, path=None):
        self.oid = oid
        self.is_complex = not isinstance(oid, six.string_types)
        self.type = type or self.default_type
        if isinstance(scale, six.string_types):
            self.scale = get_handler(
                "noc.core.script.metrics.%s" % scale
            )
        else:
            self.scale = scale
        self.path = path or []

    def iter_oids(self, script, metric):
        """
        Generator yielding oid, type, scale, path
        :param script:
        :param metric:
        :return:
        """
        if self.is_complex:
            yield tuple(self.oid), self.type, self.scale, self.path
        else:
            yield self.oid, self.type, self.scale, self.path

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

    def expand_oid(self, **kwargs):
        """
        Apply kwargs to template and return resulting oid
        :param kwargs:
        :return:
        """
        if self.is_complex:
            oids = tuple(mib[self.expand(o, kwargs)] for o in self.oid)
            if None in oids:
                return None
            else:
                return oids
        else:
            return mib[self.expand(self.oid, kwargs)]


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
class OIDsRule(object):
    """
    Multiple items for single metric
    """
    name = "oids"

    def __init__(self, oids):
        self.oids = oids

    def iter_oids(self, script, metric):
        for rule in self.oids:
            for r in rule.iter_oids(script, metric):
                yield r

    @classmethod
    def from_json(cls, data):
        if "oids" not in data:
            raise ValueError("oids is required")
        if type(data["oids"]) != list:
            raise ValueError("oids must be list")
        return OIDsRule(
            oids=[OIDRule.from_json(d) for d in data["oids"]]
        )


@six.add_metaclass(OIDRuleBase)
class MatcherRule(object):
    """
    Multiple items for single metric
    """
    name = "match"

    def __init__(self, oids, matchers):
        self.oids = oids
        self.matchers = matchers

    def iter_oids(self, script, metric):
        ctx = script.version
        for matcher, rule in self.oids:
            # match(ctx, []) always True, Priority in metrics matcher config matcher
            if (matcher is None or
                    (match(ctx, self.matchers.get(matcher, [])) and matcher in self.matchers) or
                    getattr(script, matcher, None)):
                for r in rule.iter_oids(script, metric):
                    yield r
                else:
                    # Only one match
                    break

    @classmethod
    def from_json(cls, data):
        if "$match" not in data:
            raise ValueError("Matcher is required")
        if type(data["$match"]) != list:
            raise ValueError("$match must be list")
        return MatcherRule(oids=[(d.get("$match"),
                                  OIDRule.load(d)) for d in data["$match"]],
                           matchers=data.get("$matchers", {}))


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
            g = self.normal.iter_oids
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
    Expand {{ifIndex}}
    """
    name = "ifindex"

    def iter_oids(self, script, cfg):
        if cfg.ifindex is not None:
            oid = self.expand_oid(ifIndex=cfg.ifindex)
            if oid:
                yield oid, self.type, self.scale, cfg.path


class CapabilityIndexRule(OIDRule):
    """
    Expand {{index}} to range given in capability
    capability: Integer capability containing number of iterations
    start: starting index
    """
    name = "capindex"

    def __init__(self, oid, type=None, scale=1, start=0, capability=None):
        super(CapabilityIndexRule, self).__init__(oid, type=type, scale=scale)
        self.start = start
        self.capability = capability

    def iter_oids(self, script, cfg):
        if self.capability and script.has_capability(self.capability):
            for i in range(
                self.start,
                script.capabilities[self.capability] + self.start
            ):
                oid = self.expand_oid(index=i)
                if oid:
                    yield oid, self.type, self.scale, cfg.path


class CapabilityListRule(OIDRule):
    """
    Expand {{item}} from capability
    capability: String capability, separated by *separator*
    separator: String separator, comma by default
    strip: Strip resulting item, remove spaces from both sides
    """
    name = "caplist"

    def __init__(self, oid, type=None, scale=1, capability=None,
                 separator=",", strip=True, default=None, path=None):
        super(CapabilityListRule, self).__init__(oid, type=type, scale=scale)
        self.capability = capability
        self.separator = separator
        self.strip = strip
        self.default = default
        self.path = path

    def iter_oids(self, script, cfg):
        if self.capability and script.has_capability(self.capability):
            for i in script.capabilities[self.capability].split(self.separator):
                if self.strip:
                    i = i.strip()
                if not i:
                    continue
                oid = self.expand_oid(item=i)
                path = cfg.path
                if self.path is not None and "item" in self.path:
                    path = self.path[:]
                    path[self.path.index("item")] = i
                if oid:
                    yield oid, self.type, self.scale, path
        else:
            if self.default is not None:
                oid = self.expand_oid(item=self.default)
                if oid:
                    yield oid, self.type, self.scale, cfg.path


class Script(BaseScript):
    """
    Retrieve data for topology discovery
    """
    name = "Generic.get_metrics"
    interface = IGetMetrics
    requires = []

    # Define counter types
    GAUGE = "gauge"
    COUNTER = "counter"
    #
    _SNMP_OID_RULES = {}  # Profile -> metric type ->
    _SNMP_OID_LOCK = Lock()

    def __init__(self, *args, **kwargs):
        super(Script, self).__init__(*args, **kwargs)
        self.metrics = []
        self.ts = None

    def get_snmp_metrics_get_timeout(self):
        """
        Timeout for snmp GET request
        :return:
        """
        return self.profile.snmp_metrics_get_timeout

    def get_snmp_metrics_get_chunk(self):
        """
        Aggregate up to *snmp_metrics_get_chunk* oids
        to one SNMP GET request
        :return:
        """
        return self.profile.snmp_metrics_get_chunk

    def execute(self, metrics):
        """
        Metrics is a list of:
        * id -- Opaque id, must be returned back
        * metric -- Metric type
        * path -- metric path
        * ifindex - optional ifindex
        * sla_test - optional sla test inventory
        """
        metrics = [MetricConfig(**m) for m in metrics]
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
            self.logger.debug("Make oid for metrics: %s" % m.metric)
            snmp_rule = self.get_snmp_rule(m.metric)
            if snmp_rule:
                for oid, vtype, scale, path in snmp_rule.iter_oids(self, m):
                    batch[oid] = BatchConfig(
                        id=m.id,
                        metric=m.metric,
                        path=path,
                        type=vtype,
                        scale=scale
                    )
        self.logger.debug("Batch: %s" % batch)
        # Run snmp batch
        if not batch:
            self.logger.debug("Nothing to fetch via SNMP")
            return
        # Optimize fetching, aggregating up to GET_CHUNK
        # in single request
        snmp_get_chunk = self.get_snmp_metrics_get_chunk()
        oids = set()
        for o in batch:
            if isinstance(o, six.string_types):
                oids.add(o)
            else:
                oids.update(o)
        oids = list(oids)
        results = {}  # oid -> value
        self.snmp.set_timeout_limits(self.get_snmp_metrics_get_timeout())
        while oids:
            chunk, oids = oids[:snmp_get_chunk], oids[snmp_get_chunk:]
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
            except self.snmp.FatalTimeoutError:
                self.logger.error(
                    "Fatal timeout error on: %s", oids
                )
                break
            except self.snmp.SNMPError as e:
                self.logger.error(
                    "SNMP error code %s", e.code
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
            elif callable(batch[oid].scale):
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
            bv = batch[oid]
            self.set_metric(
                id=bv.id,
                metric=bv.metric,
                value=v,
                ts=ts,
                path=bv.path,
                type=bv.type,
                scale=bv.scale
            )

    def get_ifindex(self, name):
        return self.ifindexes.get(name)

    def get_ts(self):
        """
        Returns current timestamp in nanoseconds
        """
        if not self.ts:
            self.ts = int(time.time() * NS)
        return self.ts

    def set_metric(self, id, metric, value, ts=None,
                   path=None, type="gauge", scale=1):
        """
        Append metric to output
        """
        if callable(scale):
            if not isinstance(value, list):
                value = [value]
            value = scale(*value)
            scale = 1
        self.metrics += [{
            "id": id,
            "ts": ts or self.get_ts(),
            "metric": metric,
            "path": path or [],
            "value": value,
            "type": type,
            "scale": scale
        }]

    def get_metrics(self):
        return self.metrics

    def get_snmp_rule(self, metric_type):
        profile = self.profile.name
        if profile not in self._SNMP_OID_RULES:
            self.load_snmp_rules(profile)
            self.logger.debug("Loading profile rules: %s" % self._SNMP_OID_RULES[profile])
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
