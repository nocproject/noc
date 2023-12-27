# ---------------------------------------------------------------------
# Generic.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import os
import re
import itertools
import operator
from typing import Union, Optional, List, Tuple, Callable, Dict, Any
from collections import defaultdict
from dataclasses import dataclass

# Third-party modules
import orjson

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
from noc.core.models.cfgmetrics import MetricCollectorConfig
from noc.config import config
from noc.core.perf import metrics as noc_metrics
from noc.core.mib import mib

NS = 1000_000_000.0
SNMP_OVERLOAD_VALUE = 0xFFFFFFFFFFFFFFFF  # 18446744073709551615 for 64-bit counter
PROFILES_PATH = os.path.join("sa", "profiles")


class MetricConfig(object):
    __slots__ = (
        "id",
        "metric",
        "labels",
        "oid",
        "ifindex",
        "service",
    )

    def __init__(
        self,
        id,
        metric,
        labels=None,
        oid=None,
        ifindex=None,
        service=None,
    ):
        self.id: int = id
        self.metric: str = metric
        self.labels: List[str] = labels
        self.oid: str = oid
        self.ifindex: int = ifindex
        self.service: int = service

    def __repr__(self):
        return f"<MetricConfig #{self.id} {self.metric}>"


@dataclass(frozen=True)
class ProfileMetricConfig(object):
    """
    Config for SNMP Collected metrics, supported on profile.
    """

    __slots__ = ("metric", "oid", "scale", "sla_types", "units")
    metric: str
    oid: str
    sla_types: List[str]
    scale: int
    units: str


class BatchConfig(object):
    __slots__ = ("id", "metric", "labels", "type", "scale", "units", "service")

    def __init__(self, id, metric, labels, type, scale, units, service=None):
        self.id: int = id
        self.metric: str = metric
        self.labels: List[str] = labels
        self.type: str = type
        self.scale = scale
        self.units = units
        self.service = service


# Internal sequence number for @metrics decorator ordering
_mt_seq = itertools.count(0)


def metrics(
    metrics, has_script=None, has_capability=None, matcher=None, access=None, volatile=True
):
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

    if isinstance(metrics, str):
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
            (getattr(m, n) for n in dir(m) if hasattr(getattr(m, n), "mt_seq")),
            key=operator.attrgetter("mt_seq"),
            reverse=True,
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
        m._oid_rules.update({r.name: r for r in m.OID_RULES})
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
            """
            M - Main, C - Custom, G - Generic, P - profile
            \\|G|P
            -+-+-
            M|3|1
            C|2|0
            :param s:
            :return:
            """
            if s.startswith(PROFILES_PATH):
                return 3 if "Generic" in s else 1
            else:
                return 2 if "Generic" in s else 0

        pp = script.name.rsplit(".", 1)[0]
        if pp == "Generic":
            paths = [
                p
                for p in config.get_customized_paths(
                    os.path.join("sa", "profiles", "Generic", "snmp_metrics")
                )
            ]
        else:
            v, p = pp.split(".")
            paths = sorted(
                config.get_customized_paths(
                    os.path.join("sa", "profiles", "Generic", "snmp_metrics")
                )
                + config.get_customized_paths(os.path.join("sa", "profiles", v, p, "snmp_metrics")),
                key=sort_path_key,
            )
        for path in paths:
            if not os.path.exists(path):
                continue
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f.endswith(".json"):
                        mcs.apply_snmp_rules_from_json(script, os.path.join(root, f))

    @classmethod
    def apply_snmp_rules_from_json(mcs, script, path):
        # @todo: Check read access
        with open(path) as f:
            data = f.read()
        try:
            data = orjson.loads(data)
        except ValueError as e:
            raise ValueError("Failed to parse file '%s': %s" % (path, e))
        if not isinstance(data, dict):
            raise ValueError("Error in file '%s': Must be defined as object" % path)
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
        setattr(script, fn, f)
        ff = getattr(script, fn)
        ff.__name__ = fn
        ff.__qualname__ = "%s.%s" % (script.__name__, fn)
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


class Script(BaseScript, metaclass=MetricScriptBase):
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
        OIDsRule,
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = []
        self.ts: Optional[int] = None
        # SNMP batch to be collected by collect_snmp_metrics
        # oid -> BatchConfig
        self.snmp_batch: Dict[str, List[BatchConfig]] = defaultdict(list)
        # Collected metric ids
        self.seen_ids = set()
        # get_labels_hash(metric type, labels) -> metric config
        self.metric_labels: Dict[str, List[MetricConfig]] = {}
        #
        self.sla_metrics: Dict[Tuple[str, str], int] = {}
        #
        self.cpe_metrics: Dict[Tuple[str, str], int] = {}
        # metric type -> [metric config]
        self.metric_configs: Dict[str, List[MetricConfig]] = defaultdict(list)

    def get_snmp_metrics_get_timeout(self) -> int:
        """
        Timeout for snmp GET request
        :return:
        """
        return self.profile.snmp_metrics_get_timeout

    def get_snmp_metrics_get_chunk(self) -> int:
        """
        Aggregate up to *snmp_metrics_get_chunk* oids
        to one SNMP GET request
        :return:
        """
        return self.profile.snmp_metrics_get_chunk

    @staticmethod
    def get_labels_hash(metric: str, labels: List[str]):
        if labels:
            return "\x00".join([metric] + labels)
        else:
            return metric

    def execute(
        self, metrics: Optional[List[Dict[str, Any]]] = None, collected: List[Dict[str, Any]] = None
    ):
        """
        Metrics is a list of:
        * id -- Opaque id, must be returned back
        * metric -- Metric type
        * labels -- metric labels
        * oid -- optional oid
        * ifindex - optional ifindex
        * sla_test - optional sla test inventory
        """
        # Generate list of MetricConfig from input parameters
        sla_metrics: List[MetricCollectorConfig] = []
        cpe_metrics: List[MetricCollectorConfig] = []
        sensor_metrics: List[MetricCollectorConfig] = []
        object_metrics: List[MetricConfig] = []
        if collected:
            seq_id = 1
            for coll in collected:
                coll = MetricCollectorConfig(**coll)
                if coll.collector == "sensor":
                    sensor_metrics.append(coll)
                    continue
                elif coll.collector == "sla":
                    sla_metrics.append(coll)
                    for m in coll.metrics:
                        self.sla_metrics[(coll.sla_probe, m)] = seq_id
                        seq_id += 1
                    continue
                elif coll.collector == "cpe":
                    cpe_metrics.append(coll)
                    for m in coll.metrics:
                        self.cpe_metrics[(coll.cpe, m)] = seq_id
                        seq_id += 1
                    continue
                hints = coll.get_hints()
                for m in coll.metrics:
                    object_metrics.append(
                        MetricConfig(
                            id=seq_id,
                            metric=m,
                            labels=coll.labels or [],
                            ifindex=hints.get("ifindex"),
                            service=coll.service,
                        )
                    )
                    seq_id += 1
        elif metrics:
            sm = {}
            for m in metrics:
                if m["metric"] == "Sensor | Value":
                    sensor_metrics.append(
                        MetricCollectorConfig(
                            collector="sensor",
                            metrics=["Sensor | Value"],
                            labels=m.get("labels", []),
                            sensor=m.get("sensor"),
                        )
                    )
                elif m["metric"].startswith("SLA"):
                    sla_probe = m.get("sla_probe")
                    if sla_probe not in sm:
                        sm[sla_probe] = MetricCollectorConfig(
                            collector="sla",
                            metrics=[m["metric"]],
                            labels=m.get("labels", []),
                            sla_probe=sla_probe,
                        )
                    else:
                        sm[sla_probe].metrics.append(m["metric"])
                else:
                    object_metrics.append(MetricConfig(**m))
            sla_metrics = list(sm.values())
            # metrics: List[MetricConfig] = [MetricConfig(**m) for m in metrics]
        else:
            raise ValueError("Parameter 'collected' or 'metrics' required")
        # Split by metric types
        self.metric_labels = {self.get_labels_hash(m.metric, m.labels): m for m in object_metrics}
        for m in object_metrics:
            self.metric_configs[m.metric] += [m]
        # Process metrics collection
        persistent = set()
        for m in object_metrics:
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
        # Apply sensor metrics
        if sensor_metrics:
            self.collect_sensor_metrics(sensor_metrics)
        # Apply sla metrics
        if sla_metrics:
            self.collect_sla_metrics(sla_metrics)
        if cpe_metrics:
            self.collect_cpe_metrics(cpe_metrics)
        # Apply custom metric collection processes
        self.collect_profile_metrics(object_metrics)
        return self.get_metrics()

    def clean_streaming_result(self, result):
        """
        {
            "ts": m["ts"],
            "scope": mt.scope.table_name,
            "labels": m["labels"],
            mt.field_name: m["value"],
            "_units": {mt.field_name: units},
            "managed_object": mo.bi_id,
        }
        :param result:
        :return:
        """
        data = {}
        s_data = self.streaming.get_data()
        self.streaming.data = None
        managed_object = s_data["managed_object"]
        self.script_metrics["n_metrics"] = 0
        for rr in self.metrics:
            data_mt = rr["metric"].replace(" ", "_")
            if data_mt not in s_data:
                self.logger.warning("Unknown Metric Type: %s", data_mt)
                continue
            scope_name = s_data[data_mt]["scope"]
            field_name = s_data[data_mt]["field"]
            mm = (scope_name, tuple(rr["labels"]))
            if mm not in data:
                data[mm] = {
                    "ts": rr["ts"],
                    "managed_object": managed_object,
                    "scope": scope_name,
                    "labels": rr["labels"],
                    "_units": {},
                }
                if self.streaming.utc_offset:
                    data[mm]["ts"] += self.streaming.utc_offset * NS
                if rr.get("sensor"):
                    data[mm]["sensor"] = rr["sensor"]
                if rr.get("sla_probe"):
                    data[mm]["sla_probe"] = rr["sla_probe"]
                if rr.get("service"):
                    data[mm]["service"] = rr["service"]
                if rr.get("cpe"):
                    # For CPE used ID as ManagedObject
                    data[mm]["cpe"] = rr["cpe"]
                if "time_delta" in s_data[data_mt]:
                    data[mm]["time_delta"] = s_data[data_mt]["time_delta"]
                self.script_metrics["n_metrics"] += 1
            data[mm][field_name] = rr["value"]
            data[mm]["_units"][field_name] = rr["units"]
        return list(data.values())

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
            if f.mt_access == "S" and not self.has_snmp():
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
        # pylint: disable=unnecessary-pass
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
            for oid, vtype, scale, units, labels in rule.iter_oids(self, m):
                self.snmp_batch[oid] += [
                    BatchConfig(
                        id=m.id,
                        metric=m.metric,
                        labels=labels,
                        type=vtype,
                        scale=scale,
                        units=units,
                        service=m.service,
                    )
                ]
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
            if isinstance(o, str):
                oids.add(o)
            else:
                oids.update(o)
        oids = list(oids)
        results = self.snmp.get_chunked(
            oids=oids,
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout(),
        )
        # Process results
        for oid in self.snmp_batch:
            ts = self.get_ts()
            for batch in self.snmp_batch[oid]:
                if isinstance(oid, str):
                    if oid in results:
                        v = results[oid]
                        if v is None:
                            break
                    else:
                        self.logger.error("Failed to get SNMP OID %s", oid)
                        break
                elif callable(batch.scale):
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
                            self.logger.error("Failed to get SNMP OID %s", o)
                            break
                    # Check result does not contain None
                    if len(v) < len(oid):
                        self.logger.error(
                            "Cannot calculate complex value for %s " "due to missed values: %s",
                            oid,
                            v,
                        )
                        continue
                else:
                    self.logger.error(
                        "Cannot evaluate complex oid %s. " "Scale must be callable", oid
                    )
                    continue
                bv = batch
                self.set_metric(
                    id=bv.id,
                    metric=bv.metric,
                    value=v,
                    ts=ts,
                    labels=bv.labels,
                    type=bv.type,
                    scale=bv.scale,
                    units=bv.units,
                    service=bv.service,
                )

    def get_ifindex(self, name):
        return self.ifindexes.get(name)

    def get_ts(self) -> int:
        """
        Returns current timestamp in nanoseconds
        """
        if not self.ts:
            self.ts = int(time.time() * NS)
        return self.ts

    def set_metric(
        self,
        id: Union[int, Tuple[str, Optional[List[str]]]],
        metric: str = None,
        value: Union[int, float] = 0,
        ts: Optional[int] = None,
        labels: Optional[Union[List[str], Tuple[str]]] = None,
        type: str = "gauge",
        scale: Union[float, int, Callable] = 1,
        units: str = "1",
        multi: bool = False,
        sensor: Optional[int] = None,
        sla_probe: Optional[int] = None,
        cpe: Optional[int] = None,
        service: Optional[int] = None,
    ):
        """
        Append metric to output
        :param id:
            Opaque id, as in request.
            May be tuple of (metric, labels), then it will be resolved automatically
            and *metric* and *labels* parameters may be ommited
        :param metric: Metric type as string.
            When None, try to get metric type from id tuple
        :param value: Measured value
        :param ts: Timestamp (nanoseconds precision)
        :param labels: labels. Either as requested, or refined.
            When None, try to get from id tuple
        :param type:
            Measure type. Possible values:
            "gauge"
            "counter"
            "delta"
            "bool"
        :param scale: Metric scale (Multiplier to be applied after all processing).
            When callable, function will be called, passing value as positional argument
        :param units: Metric MeasurementUnit code. Default - Scalar
            Possible values from menu: Performance Management -> Setup -> Measurement Unit
        :param multi: True if single request can return several different labels.
            When False - only first call with composite labels for same labels will be returned
        :param sensor: Sensor Id
        :param sla_probe: SLA Probe Id
        :param cpe: CPE Id
        :param service: Service Id
        """
        if value == SNMP_OVERLOAD_VALUE:
            self.logger.debug("SNMP Counter is full. Skipping value...")
            noc_metrics["error", ("type", "snmp_overload_drops")] += 1
            return
        if callable(scale):
            if not isinstance(value, list):
                value = [value]
            value = scale(*value)
            scale = 1
        if sensor and sensor in self.seen_ids:
            return
        elif sla_probe and (sla_probe, metric) in self.sla_metrics:
            id = self.sla_metrics[(sla_probe, metric)]
        elif sla_probe:
            return
        elif isinstance(id, tuple):
            # Composite id, extract type and labels and resolve
            if not metric:
                metric = id[0]
            if not labels:
                labels = id[1]
            mc = self.metric_labels.get(self.get_labels_hash(*id))
            if not mc:
                # Not requested, ignoring
                self.logger.info("Not requesting, ignoring")
                return
            id = mc.id
            if not multi and id in self.seen_ids:
                return  # Already seen
        self.script_metrics["n_measurements"] += 1
        self.metrics += [
            {
                "id": id,
                "ts": ts or self.get_ts(),
                "metric": metric,
                "labels": labels or [],
                "value": value,
                "type": type,
                "units": units,
                # "scale": scale,
                "sensor": sensor,
                "sla_probe": sla_probe,
                "cpe": cpe,
                "service": service,
            }
        ]
        self.seen_ids.add(id)

    def get_metrics(self):
        self.script_metrics["n_metrics"] = len(self.metrics)
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
        ["Interface | Last Сhange"],
        volatile=False,
        access="S",
    )
    def get_interface_lastchange(self, metrics):
        uptime = self.snmp.get("1.3.6.1.2.1.1.3.0")
        oids = {mib["IF-MIB::ifLastChange", str(m.ifindex)]: m for m in metrics if m.ifindex}
        result = self.snmp.get_chunked(
            oids=list(oids),
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout(),
        )
        ts = self.get_ts()
        for r in result:
            mc = oids[r]
            self.set_metric(
                id=mc.id,
                metric=mc.metric,
                value=(int(int(uptime - result[r]) / 8640000)),
                ts=ts,
                labels=mc.labels,
            )

    SENSOR_OID_SCALE: Dict[str, Union[int, Callable]] = {}  # oid -> scale

    def collect_sensor_metrics(self, metrics: List[MetricCollectorConfig]):
        """
        Collect sensor metrics method. Configured by profile
        :param metrics:
        :return:
        """
        for sensor in metrics:
            hints = sensor.get_hints()
            if "oid" not in hints:
                # Not collected hints
                continue
            try:
                value = self.snmp.get(hints["oid"])
                self.set_metric(
                    id=sensor.sensor,
                    metric="Sensor | Value",
                    labels=sensor.labels,
                    value=float(value),
                    scale=self.SENSOR_OID_SCALE.get(hints["oid"], 1),
                    sensor=sensor.sensor,
                )
            except Exception:
                continue

    def collect_sla_metrics(self, metrics: List[MetricCollectorConfig]):
        """
        Collect for SLA metrics method. Replaced by profile
        :param metrics:
        :return:
        """
        ...

    def collect_cpe_metrics(self, metrics: List[MetricCollectorConfig]):
        """
        Collect for CPE metrics method. Replaced by profile
        :param metrics:
        :return:
        """
        ...

    # @metrics(
    #     [
    #         "Interface | DOM | RxPower",
    #         "Interface | DOM | Temperature",
    #         "Interface | DOM | TxPower",
    #         "Interface | DOM | Voltage",
    #     ],
    #     has_capability="DB | Interfaces",
    #     has_script="get_dom_status",
    #     access="C",  # CLI version
    #     volatile=False,
    # )
    # def collect_dom_metrics(self, metrics):
    #     r = {}
    #     for m in self.scripts.get_dom_status():
    #         ipath = ["", "", "", m["interface"]]
    #         if m.get("temp_c") is not None:
    #             self.set_metric(id=("Interface | DOM | Temperature", ipath), value=m["temp_c"])
    #         if m.get("voltage_v") is not None:
    #             self.set_metric(id=("Interface | DOM | Voltage", ipath), value=m["voltage_v"])
    #         if m.get("optical_rx_dbm") is not None:
    #             self.set_metric(id=("Interface | DOM | RxPower", ipath), value=m["optical_rx_dbm"])
    #         if m.get("current_ma") is not None:
    #             self.set_metric(id=("Interface | DOM | Bias Current", ipath), value=m["current_ma"])
    #         if m.get("optical_tx_dbm") is not None:
    #             self.set_metric(id=("Interface | DOM | TxPower", ipath), value=m["optical_tx_dbm"])
    #     return r
