# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import os
import re
import itertools
import operator
from collections import defaultdict
# Third-party modules
import six
import ujson
# NOC modules
from noc.core.script.base import BaseScript, BaseScriptMetaclass
from noc.sa.interfaces.igetmetrics import IGetMetrics
from noc.core.script.oidrules.oid import OIDRule
from noc.core.script.oidrules.bool import BooleanRule
from noc.core.script.oidrules.capindex import CapabilityIndexRule
from noc.core.script.oidrules.caplist import CapabilityListRule
from noc.core.script.oidrules.caps import CapabilityRule
from noc.core.script.oidrules.counter import CounterRule
from noc.core.script.oidrules.hires import HiresRule
from noc.core.script.oidrules.ifindex import InterfaceRule
from noc.core.script.oidrules.match import MatcherRule
from noc.core.script.oidrules.oids import OIDsRule
from noc.core.script.oidrules.loader import load_rule, with_resolver
from noc.config import config

NS = 1000000000.0


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


# Internal sequence number for @metrics decorator ordering
_mt_seq = itertools.count(0)


def metrics(metrics, has_script=None, has_capability=None,
            matcher=None, access=None, volatile=True):
    """
    Decorator to use inside get_metrics script to denote functions
    which can return set of metrics

    @metrics(["Metric Type1", "Metric Type2"])
    def get_custom_metrics(self, metrics):
        ...
        self.set_metric(...)
        ...

    NB: set_metric() function applies metrics to local context.
    @metrics decorator maps requested and applicable metrics to global result
    Handler accepts *metrics* parameter containing list of MetricConfig
    applicable to its types

    :param metrics: string or list of metric type names
    :param has_script: Match only if object has script
    :param has_capability: Match only if object has capability
    :param matcher: Match only if object fits to matcher
    :param access: Required access. Should be
        * S - for SNMP-only
        * C - for CLI-only
        * None - always match
    :param volatile: True - Function call results may be changed over time
        False - Function call results are persistent.
        Function may be called only once
    :return: None
    """
    def wrapper(f):
        f.mt_seq = next(_mt_seq)
        f.mt_metrics = metrics
        f.mt_has_script = has_script
        f.mt_has_capability = has_capability
        f.mt_matcher = matcher
        f.mt_access = access
        f.mt_volatile = volatile
        return f

    if isinstance(metrics, six.string_types):
        metrics = [metrics]
    assert isinstance(metrics, list), "metrics must be string or list"
    return wrapper


class MetricScriptBase(BaseScriptMetaclass):
    """
    get_metrics metaclass. Performs @metrics decorator processing
    """
    def __new__(mcs, name, bases, attrs):
        m = super(MetricScriptBase, mcs).__new__(mcs, name, bases, attrs)
        # Inject metric_type -> [handler] mappings
        m._mt_map = defaultdict(list)
        # Get @metrics handlers
        for h in sorted(
            (
                getattr(m, n) for n in dir(m)
                if hasattr(getattr(m, n), "mt_seq")
            ),
            key=operator.attrgetter("mt_seq"),
            reverse=True
        ):
            for mt in h.mt_metrics:
                m._mt_map[mt] += [h]
        # Install oid rules
        # Instantiate from base class' OID_RULES
        parent_rules = getattr(bases[0], "_oid_rules", None)
        if parent_rules:
            m._oid_rules = parent_rules.copy()
        else:
            m._oid_rules = {}
        # Append own rules from OID_RULES
        m._oid_rules.update(dict((r.name, r) for r in m.OID_RULES))
        # Load snmp_metrics/*.json
        with with_resolver(m.get_oid_rule):
            mcs.apply_snmp_rules(m)
        return m

    @classmethod
    def apply_snmp_rules(mcs, script):
        """
        Initialize SNMP rules from JSON
        :param script: Script class
        :return:
        """
        def sort_path_key(s):
            k1, k2 = 1, 1
            if s.startswith(os.path.join("sa", "profiles")):
                k1 = 0
            if "Generic" in s:
                k2 = 0
            return k1, k2
        pp = script.name.rsplit(".", 1)[0]
        if pp == "Generic":
            paths = [p for p in config.get_customized_paths(
                os.path.join("sa", "profiles", "Generic", "snmp_metrics"))]
        else:
            v, p = pp.split(".")
            paths = sorted(config.get_customized_paths(os.path.join("sa", "profiles", "Generic", "snmp_metrics")) +
                           config.get_customized_paths(os.path.join("sa", "profiles", v, p, "snmp_metrics")),
                           key=sort_path_key)
        for path in paths:
            if not os.path.exists(path):
                continue
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f.endswith(".json"):
                        mcs.apply_snmp_rules_from_json(
                            script,
                            os.path.join(root, f)
                        )

    @classmethod
    def apply_snmp_rules_from_json(mcs, script, path):
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
        script._mt_map[data["$metric"]] += [
            mcs.get_snmp_handler(script, data["$metric"], load_rule(data))
        ]

    @classmethod
    def get_snmp_handler(mcs, script, metric, rule):
        """
        Generate SNMP handler for @metrics
        """
        def f(self, metrics):
            self.schedule_snmp_oids(rule, metric, metrics)

        fn = mcs.get_snmp_handler_name(metric)
        f.mt_has_script = None
        f.mt_has_capability = "SNMP"
        f.mt_matcher = None
        f.mt_access = "S"
        f.mt_volatile = False
        setattr(script, fn, six.create_unbound_method(f, script))
        ff = getattr(script, fn)
        ff.__func__.__name__ = fn
        return ff

    rx_mt_name = re.compile("[^a-z0-9]+")

    @classmethod
    def get_snmp_handler_name(mcs, metric):
        """
        Generate python function name
        :param metric:
        :return:
        """
        return "get_snmp_json_%s" % mcs.rx_mt_name.sub("_", str(metric.lower()))


@six.add_metaclass(MetricScriptBase)
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

    OID_RULES = [
        OIDRule,
        BooleanRule,
        CapabilityIndexRule,
        CapabilityListRule,
        CapabilityRule,
        CounterRule,
        HiresRule,
        InterfaceRule,
        MatcherRule,
        OIDsRule
    ]

    def __init__(self, *args, **kwargs):
        super(Script, self).__init__(*args, **kwargs)
        self.metrics = []
        self.ts = None
        # SNMP batch to be collected by collect_snmp_metrics
        # oid -> BatchConfig
        self.snmp_batch = {}
        # Collected metric ids
        self.seen_ids = set()
        # get_path_hash(metric type, path) -> metric config
        self.paths = {}
        # metric type -> [metric config]
        self.metric_configs = defaultdict(list)

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

    @staticmethod
    def get_path_hash(metric, path):
        if path:
            return "\x00".join([metric] + [str(x) for x in path])
        else:
            return metric

    def execute(self, metrics):
        """
        Metrics is a list of:
        * id -- Opaque id, must be returned back
        * metric -- Metric type
        * path -- metric path
        * ifindex - optional ifindex
        * sla_test - optional sla test inventory
        """
        # Generate list of MetricConfig from input parameters
        metrics = [MetricConfig(**m) for m in metrics]
        # Split by metric types
        self.paths = dict(
            (self.get_path_hash(m.metric, m.path), m)
            for m in metrics
        )
        for m in metrics:
            self.metric_configs[m.metric] += [m]
        # Process metrics collection
        persistent = set()
        for m in metrics:
            if m.id in self.seen_ids:
                self.logger.debug("[%s] Metric type is already collected. Skipping", m.metric)
                continue  # Already collected
            if m.metric not in self._mt_map:
                self.logger.debug("[%s] Metric type is not supported. Skipping", m.metric)
                continue
            # Call handlers
            for h in self.iter_handlers(m.metric):
                hid = id(h)
                if not h.mt_volatile and hid in persistent:
                    continue  # persistent function already called
                h(self, self.metric_configs[m.metric])
                if not h.mt_volatile:
                    persistent.add(hid)
                if m.id in self.seen_ids:
                    break  # Metric collected
        # Request snmp metrics from box
        if self.snmp_batch:
            self.collect_snmp_metrics()
        # Apply custom metric collection processes
        self.collect_profile_metrics(metrics)
        return self.get_metrics()

    def iter_handlers(self, metric):
        """
        Generator yilding possible handlers for metrics collection in order of preference
        :param metric: Metric type name
        :return: callable accepting *metrics*
        """
        def is_applicable(f):
            if f.mt_has_script and f.mt_has_script not in self.scripts:
                return False
            if f.mt_has_capability and not self.has_capability(f.mt_has_capability):
                return False
            if f.mt_matcher and not getattr(self, f.mt_matcher, False):
                return False
            return True

        pref = self.get_access_preference()
        handlers = self._mt_map[metric]
        pri = pref[0]
        sec = pref[1] if len(pref) > 1 else None
        # Iterate primary method
        for h in handlers:
            if (not h.mt_access or h.mt_access == pri) and is_applicable(h):
                yield h
        # Iterate secondary method
        if sec:
            for h in handlers:
                if h.mt_access == sec and is_applicable(h):
                    yield h

    def collect_profile_metrics(self, metrics):
        """
        Profile extension for very custom logic
        """
        pass

    def schedule_snmp_oids(self, rule, metric, metrics):
        """
        Schedule SNMP oid collection for given metrics.
        Used as partial function to build @metrics handler
        for JSON snmp rules

        :param rule: OIDRule instance
        :param metrics: List of MetricConfig instances
        :return:
        """
        for m in self.metric_configs[metric]:
            for oid, vtype, scale, path in rule.iter_oids(self, m):
                self.snmp_batch[oid] = BatchConfig(
                    id=m.id,
                    metric=m.metric,
                    path=path,
                    type=vtype,
                    scale=scale
                )
                # Mark as seen to stop further processing
                self.seen_ids.add(m.id)

    def collect_snmp_metrics(self):
        """
        Collect all scheduled SNMP metrics
        """

        # Run snmp batch
        if not self.snmp_batch:
            self.logger.debug("Nothing to fetch via SNMP")
            return
        # Build list of oids
        oids = set()
        for o in self.snmp_batch:
            if isinstance(o, six.string_types):
                oids.add(o)
            else:
                oids.update(o)
        oids = list(oids)
        results = self.snmp.get_chunked(
            oids=oids,
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout()
        )
        # Process results
        for oid in self.snmp_batch:
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
            elif callable(self.snmp_batch[oid].scale):
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
            bv = self.snmp_batch[oid]
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

    def set_metric(self, id, metric=None, value=0, ts=None,
                   path=None, type="gauge", scale=1, multi=False):
        """
        Append metric to output
        :param id:
            Opaque id, as in request.
            May be tuple of (metric, path), then it will be resolved automatically
            and *metric* and *path* parameters may be ommited
        :param metric: Metric type as string.
            When None, try to get metric type from id tuple
        :param value: Measured value
        :param ts: Timestamp (nanoseconds precision)
        :param path: Path. Either as requested, or refined.
            When None, try to get from id tuple
        :param type:
            Measure type. Possible values:
            "gauge"
            "counter"
            "delta"
            "bool"
        :param scale: Metric scale (Multiplier to be applied after all processing).
            When callable, function will be called, passing value as positional argument
        :param multi: True if single request can return several different paths.
            When False - only first call with composite path for same path will be returned
        """
        if callable(scale):
            if not isinstance(value, list):
                value = [value]
            value = scale(*value)
            scale = 1
        if isinstance(id, tuple):
            # Composite id, extract type and path and resolve
            if not metric:
                metric = id[0]
            if not path:
                path = id[1]
            mc = self.paths.get(self.get_path_hash(*id))
            if not mc:
                # Not requested, ignoring
                self.logger.info("Not requesting, ignoring")
                return
            id = mc.id
            if not multi and id in self.seen_ids:
                return  # Already seen
        self.metrics += [{
            "id": id,
            "ts": ts or self.get_ts(),
            "metric": metric,
            "path": path or [],
            "value": value,
            "type": type,
            "scale": scale
        }]
        self.seen_ids.add(id)

    def get_metrics(self):
        return self.metrics

    @classmethod
    def get_oid_rule(cls, name):
        """
        Returns OIDRule type by its name
        :param name: oid rule type name
        :return: OIDRule descendant or None
        """
        return cls._oid_rules.get(name)

    @metrics(
        ["Interface | DOM | RxPower",
         "Interface | DOM | Temperature", "Interface | DOM | TxPower",
         "Interface | DOM | Voltage"],
        has_capability="DB | Interfaces",
        has_script="get_dom_status",
        access="C",  # CLI version
        volatile=False
    )
    def collect_dom_metrics(self, metrics):
        r = {}
        for m in self.scripts.get_dom_status():
            ipath = ["", "", "", m["interface"]]
            if m.get("temp_c") is not None:
                self.set_metric(id=("Interface | DOM | Temperature", ipath),
                                value=m["temp_c"])
            if m.get("voltage_v") is not None:
                self.set_metric(id=("Interface | DOM | Voltage", ipath),
                                value=m["voltage_v"])
            if m.get("optical_rx_dbm") is not None:
                self.set_metric(id=("Interface | DOM | RxPower", ipath),
                                value=m["optical_rx_dbm"])
            if m.get("current_ma") is not None:
                self.set_metric(id=("Interface | DOM | Bias Current", ipath),
                                value=m["current_ma"])
            if m.get("optical_tx_dbm") is not None:
                self.set_metric(id=("Interface | DOM | TxPower", ipath),
                                value=m["optical_tx_dbm"])
        return r
