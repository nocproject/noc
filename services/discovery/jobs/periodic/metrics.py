# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Metric collector
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
from collections import namedtuple
import itertools
import time
from collections import defaultdict
# Third-party modules
import six
import cachetools
from pymongo import ReadPreference
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.pm.models.metrictype import MetricType
from noc.sla.models.slaprofile import SLAProfile
from noc.sla.models.slaprobe import SLAProbe
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.pm.models.thresholdprofile import ThresholdProfile
from noc.core.window import get_window_function
from noc.core.handler import get_handler


MAX31 = 0x7FFFFFFF
MAX32 = 0xFFFFFFFF
MAX64 = 0xFFFFFFFFFFFFFFFF

NS = 1000000000.0

MT_COUNTER = "counter"
MT_BOOL = "bool"
MT_DELTA = "delta"
MT_COUNTER_DELTA = set([MT_COUNTER, MT_DELTA])

WT_MEASURES = "m"
WT_TIME = "t"

SCOPE_OBJECT = "object"
SCOPE_INTERFACE = "interface"
SCOPE_SLA = "sla"

metrics_lock = Lock()

MetricConfig = namedtuple("MetricConfig", [
    "metric_type",
    "enable_box", "enable_periodic",
    "is_stored",
    "window_type", "window", "window_function", "window_config",
    "window_related",
    "low_error", "low_warn", "high_warn", "high_error",
    "low_error_severity", "low_warn_severity", "high_warn_severity", "high_error_severity",
    "threshold_profile",
    "process_thresholds"
])


class MData(object):
    __slots__ = (
        "id",
        "ts",
        "metric",
        "path",
        "value",
        "scale",
        "type",
        "abs_value",
        "label"
    )

    def __init__(self, id, ts, metric, path=None, value=None,
                 scale=None, type=None, abs_value=None):
        self.id = id
        self.ts = ts
        self.metric = metric
        self.path = path
        self.value = value
        self.scale = scale
        self.type = type
        self.abs_value = abs_value
        if path:
            self.label = "%s|%s" % (
                metric,
                "|".join(str(p) for p in path)
            )
        else:
            self.label = metric

    def __repr__(self):
        return "<MData #%s %s>" % (self.id, self.metric)


class MetricsCheck(DiscoveryCheck):
    """
    MAC discovery
    """
    name = "metrics"
    required_script = "get_metrics"

    _object_profile_metrics = cachetools.TTLCache(1000, 60)
    _interface_profile_metrics = cachetools.TTLCache(1000, 60)
    _slaprofile_metrics = cachetools.TTLCache(1000, 60)

    S_OK = 0
    S_WARN = 1
    S_ERROR = 2

    SMAP = {
        0: "ok",
        1: "warn",
        2: "error"
    }

    SEV_MAP = {
        1: 2000,
        2: 3000
    }

    AC_PM_THRESHOLDS = AlarmClass.get_by_name("NOC | PM | Out of Thresholds")
    AC_PM_LOW_ERROR = AlarmClass.get_by_name("NOC | PM | Low Error")
    AC_PM_HIGH_ERROR = AlarmClass.get_by_name("NOC | PM | High Error")
    AC_PM_LOW_WARN = AlarmClass.get_by_name("NOC | PM | Low Warning")
    AC_PM_HIGH_WARN = AlarmClass.get_by_name("NOC | PM | High Warning")

    SLA_CAPS = [
        "Cisco | IP | SLA | Probes"
    ]

    def __init__(self, *args, **kwargs):
        super(MetricsCheck, self).__init__(*args, **kwargs)
        self.id_count = itertools.count()
        self.id_metrics = {}

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_object_profile_metrics"),
        lock=lambda _: metrics_lock
    )
    def get_object_profile_metrics(cls, p_id):
        r = {}
        opr = ManagedObjectProfile.get_by_id(id=p_id)
        if not opr:
            return r
        for m in opr.metrics:
            mt_id = m.get("metric_type")
            if not mt_id:
                continue
            mt = MetricType.get_by_id(mt_id)
            if not mt:
                continue
            le = m.get("low_error")
            lw = m.get("low_warn")
            he = m.get("high_error")
            hw = m.get("high_warn")
            lew = AlarmSeverity.severity_for_weight(int(m.get("low_error_weight", 10)))
            lww = AlarmSeverity.severity_for_weight(int(m.get("low_warn_weight", 1)))
            hew = AlarmSeverity.severity_for_weight(int(m.get("high_error_weight", 1)))
            hww = AlarmSeverity.severity_for_weight(int(m.get("high_warn_weight", 10)))
            threshold_profile = None
            if m.get("threshold_profile"):
                threshold_profile = ThresholdProfile.get_by_id(m.get("threshold_profile"))
            r[mt.name] = MetricConfig(
                mt,
                m.get("enable_box", True),
                m.get("enable_periodic", True),
                m.get("is_stored", True),
                m.get("window_type", "m"),
                int(m.get("window", 1)),
                m.get("window_function", "last"),
                m.get("window_config"),
                m.get("window_related", False),
                int(le) if le is not None else None,
                int(lw) if lw is not None else None,
                int(hw) if hw is not None else None,
                int(he) if he is not None else None,
                lew, lww, hww, hew,
                threshold_profile,
                le is not None or lw is not None or he is not None or hw is not None
            )
        return r

    @staticmethod
    def quote_path(path):
        """
        Convert path list to ClickHouse format
        :param path:
        :return:
        """
        return "[%s]" % ",".join("'%s'" % p for p in path)

    @staticmethod
    def config_from_settings(m):
        """
        Returns MetricConfig from .metrics field
        :param m:
        :return:
        """
        return MetricConfig(
            m.metric_type,
            m.enable_box, m.enable_periodic,
            m.is_stored,
            m.window_type, m.window, m.window_function,
            m.window_config, m.window_related,
            m.low_error, m.low_warn, m.high_warn, m.high_error,
            AlarmSeverity.severity_for_weight(m.low_error_weight),
            AlarmSeverity.severity_for_weight(m.low_warn_weight),
            AlarmSeverity.severity_for_weight(m.high_warn_weight),
            AlarmSeverity.severity_for_weight(m.high_error_weight),
            m.threshold_profile,
            m.low_error is not None or m.low_warn is not None or m.high_warn is not None or m.high_error is not None
        )

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_interface_profile_metrics"),
        lock=lambda _: metrics_lock
    )
    def get_interface_profile_metrics(cls, p_id):
        r = {}
        ipr = InterfaceProfile.get_by_id(id=p_id)
        if not ipr:
            return r
        for m in ipr.metrics:
            r[m.metric_type.name] = cls.config_from_settings(m)
        return r

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_slaprofile_metrics"),
        lock=lambda _: metrics_lock)
    def get_slaprofile_metrics(cls, p_id):
        r = {}
        spr = SLAProfile.get_by_id(p_id)
        if not spr:
            return r
        for m in spr.metrics:
            r[m.metric_type.name] = cls.config_from_settings(m)
        return r

    def get_object_metrics(self):
        """
        Populate metrics list with objects metrics
        :return:
        """
        metrics = []
        o_metrics = self.get_object_profile_metrics(self.object.object_profile.id)
        self.logger.debug("Object metrics: %s", o_metrics)
        for metric in o_metrics:
            if ((self.is_box and not o_metrics[metric].enable_box) or
                    (self.is_periodic and not o_metrics[metric].enable_periodic)):
                continue
            m_id = next(self.id_count)
            metrics += [{
                "id": m_id,
                "metric": metric
            }]
            self.id_metrics[m_id] = o_metrics[metric]
        if not metrics:
            self.logger.info("Object metrics are not configured. Skipping")
        return metrics

    def get_subinterfaces(self):
        subs = defaultdict(list)  # interface id -> [{"name":, "ifindex":}]
        for si in SubInterface._get_collection().with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED
        ).find({
            "managed_object": self.object.id
        }, {
            "name": 1,
            "interface": 1,
            "ifindex": 1
        }):
            subs[si["interface"]] += [{
                "name": si["name"],
                "ifindex": si.get("ifindex")
            }]
        return subs

    def get_interface_metrics(self):
        """
        Populate metrics list with interface metrics
        :return:
        """
        subs = None
        metrics = []
        for i in Interface._get_collection().with_options(
                read_preference=ReadPreference.SECONDARY_PREFERRED
        ).find({
            "managed_object": self.object.id,
            "type": "physical"
        }, {
            "_id": 1,
            "name": 1,
            "ifindex": 1,
            "profile": 1
        }):
            ipr = self.get_interface_profile_metrics(i["profile"])
            self.logger.debug("Interface %s. ipr=%s", i["name"], ipr)
            if not ipr:
                continue  # No metrics configured
            i_profile = InterfaceProfile.get_by_id(i["profile"])
            if i_profile.allow_subinterface_metrics and subs is None:
                # Resolve subinterfaces
                subs = self.get_subinterfaces()
            ifindex = i.get("ifindex")
            for metric in ipr:
                if ((self.is_box and not ipr[metric].enable_box) or
                        (self.is_periodic and not ipr[metric].enable_periodic)):
                    continue
                m_id = next(self.id_count)
                m = {
                    "id": m_id,
                    "metric": metric,
                    "path": ["", "", "", i["name"]]
                }
                if ifindex is not None:
                    m["ifindex"] = ifindex
                metrics += [m]
                self.id_metrics[m_id] = ipr[metric]
                if i_profile.allow_subinterface_metrics:
                    for si in subs[i["_id"]]:
                        m_id = next(self.id_count)
                        m = {
                            "id": m_id,
                            "metric": metric,
                            "path": ["", "", "", i["name"], si["name"]]
                        }
                        if si["ifindex"] is not None:
                            m["ifindex"] = si["ifindex"]
                        metrics += [m]
                        self.id_metrics[m_id] = ipr[metric]
        if not metrics:
            self.logger.info("Interface metrics are not configured. Skipping")
        return metrics

    def get_sla_metrics(self):
        if not self.has_any_capability(self.SLA_CAPS):
            self.logger.info("SLA not configured, skipping SLA metrics")
        metrics = []
        for p in SLAProbe._get_collection().with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED
        ).find({
            "managed_object": self.object.id
        }, {
            "name": 1,
            "group": 1,
            "profile": 1,
            "type": 1
        }):
            if not p.get("profile"):
                self.logger.debug("Probe %s has no profile. Skipping", p["name"])
                continue
            pm = self.get_slaprofile_metrics(p["profile"])
            if not pm:
                self.logger.debug(
                    "Probe %s has profile '%s' with no configured metrics. "
                    "Skipping", p["name"], p.profile.name
                )
                continue
            for metric in pm:
                if ((self.is_box and not pm[metric].enable_box) or
                        (self.is_periodic and not pm[metric].enable_periodic)):
                    continue
                m_id = next(self.id_count)
                metrics += [{
                    "id": m_id,
                    "metric": metric,
                    "path": [p.get("group", ""), p["name"]],
                    "sla_type": p["type"]
                }]
                self.id_metrics[m_id] = pm[metric]
        if not metrics:
            self.logger.info("SLA metrics are not configured. Skipping")
        return metrics

    def process_result(self, result):
        """
        Process IGetMetrics result
        :param result:
        :return:
        """
        # Restore last counter state
        if self.has_artefact("reboot"):
            self.logger.info(
                "Resetting counter context due to detected reboot"
            )
            self.job.context["counters"] = {}
        counters = self.job.context["counters"]
        alarms = []
        data = defaultdict(dict)
        n_metrics = 0
        mo_id = self.object.bi_id
        ts_cache = {}  # timestamp -> (date, ts)
        #
        for m in result:
            path = m.path
            cfg = self.id_metrics.get(m.id)
            if m.type in MT_COUNTER_DELTA:
                # Counter type
                if path:
                    key = "%x|%s" % (
                        cfg.metric_type.bi_id,
                        "|".join(str(p) for p in path)
                    )
                else:
                    key = "%x" % cfg.metric_type.bi_id
                # Restore old value and save new
                r = counters.get(key)
                counters[key] = (m.ts, m.value)
                if r is None:
                    # No stored state
                    self.logger.debug(
                        "[%s] COUNTER value is not found. "
                        "Storing and waiting for a new result",
                        m.label
                    )
                    continue
                # Calculate counter
                self.logger.debug(
                    "[%s] Old value: %s@%s, new value: %s@%s.",
                    m.label, r[1], r[0], m.value, m.ts
                )
                if m.type == MT_COUNTER:
                    cv = self.convert_counter(m, r)
                else:
                    cv = self.convert_delta(m, r)
                if cv is None:
                    # Counter stepback or other errors
                    # Remove broken value
                    self.logger.debug(
                        "[%s] Counter stepback from %s@%s to %s@%s: Skipping",
                        m.label, r[1], r[0], m.value, m.ts
                    )
                    del counters[key]
                    continue
                m.value = cv
                m.abs_value = cv * m.scale
            elif m.type == MT_BOOL:
                # Convert boolean type
                m.abs_value = 1 if m.value else 0
            else:
                # Gauge
                m.abs_value = m.value * m.scale

            self.logger.debug(
                "[%s] Measured value: %s. Scale: %s. Resulting value: %s",
                m.label, m.value, m.scale, m.abs_value
            )
            # Schedule to store
            if cfg.is_stored:
                tsc = ts_cache.get(m.ts)
                if not tsc:
                    lt = time.localtime(m.ts // 1000000000)
                    tsc = (
                        time.strftime("%Y-%m-%d", lt),
                        time.strftime("%Y-%m-%d %H:%M:%S", lt)
                    )
                    ts_cache[m.ts] = tsc
                if path:
                    pk = "%s\t%s\t%d\t%s" % (
                        tsc[0], tsc[1], mo_id,
                        self.quote_path(path)
                    )
                    table = "%s.date.ts.managed_object.path" % cfg.metric_type.scope.table_name
                else:
                    pk = "%s\t%s\t%d" % (tsc[0], tsc[1], mo_id)
                    table = "%s.date.ts.managed_object" % cfg.metric_type.scope.table_name
                field = cfg.metric_type.field_name
                try:
                    data[table, pk][field] = cfg.metric_type.clean_value(m.abs_value)
                except ValueError as e:
                    self.logger.info(
                        "[%s] Cannot clean value %s: %s",
                        m.label, m.abs_value, e
                    )
                    continue
                n_metrics += 1
            if cfg.process_thresholds and m.abs_value is not None:
                alarms += self.process_thresholds(m, cfg)
        return n_metrics, data, alarms

    def handler(self):
        self.logger.info("Collecting metrics")
        # Build get_metrics input parameters
        metrics = self.get_object_metrics()
        metrics += self.get_interface_metrics()
        metrics += self.get_sla_metrics()
        if not metrics:
            self.logger.info("No metrics configured. Skipping")
            return
        # Collect metrics
        self.logger.debug("Collecting metrics: %s", metrics)

        result = [
            MData(**r)
            for r in self.object.scripts.get_metrics(metrics=metrics)
        ]
        if not result:
            self.logger.info("No metrics found")
            return
        # Process results
        n_metrics, data, alarms = self.process_result(result)
        # Send metrics
        if n_metrics:
            self.logger.info("Spooling %d metrics", n_metrics)
            self.send_metrics(data)
        # Set up threshold alarms
        self.logger.info("%d alarms detected", len(alarms))
        self.job.update_umbrella(
            self.AC_PM_THRESHOLDS,
            alarms
        )

    def convert_delta(self, m, r):
        """
        Calculate value from delta, gently handling overflows
        :param m: MData
        :param r: Old state (ts, value)
        """
        if m.value < r[1]:
            # Counter decreased, either due wrap or stepback
            if r[1] <= MAX31:
                mc = MAX31
            elif r[1] <= MAX32:
                mc = MAX32
            else:
                mc = MAX64
            # Direct distance
            d_direct = r[1] - m.value
            # Wrap distance
            d_wrap = m.value + (mc - r[1])
            if d_direct < d_wrap:
                # Possible counter stepback
                # Skip value
                self.logger.debug(
                    "[%s] Counter stepback: %s -> %s",
                    m.label, r[1], m.value
                )
                return None
            else:
                # Counter wrap
                self.logger.debug(
                    "[%s] Counter wrap: %s -> %s",
                    m.label, r[1], m.value
                )
                return d_wrap
        else:
            return m.value - r[1]

    def convert_counter(self, m, r):
        """
        Calculate value from counter, gently handling overflows
        :param m: MData
        :param r: Old state (ts, value)
        """
        dt = (float(m.ts) - float(r[0])) / NS
        delta = self.convert_delta(m, r)
        if delta is None:
            return delta
        return float(delta) / dt

    def get_window_function(self, m, cfg):
        """
        Check thresholds
        :param m: dict with metric result
        :param cfg: MetricConfig
        :return: Value or None
        """
        # Build window state key
        if m.path:
            key = "%x|%s" % (
                cfg.metric_type.bi_id,
                "|".join(str(p) for p in m.path)
            )
        else:
            key = "%x" % cfg.metric_type.bi_id
        #
        states = self.job.context["metric_windows"]
        value = m.abs_value
        ts = m.ts // 1000000000
        # Do not store single-value windows
        drop_window = cfg.window_type == "m" and cfg.window == 1
        # Restore window
        if drop_window:
            window = [(ts, value)]
            window_full = True
            if key in states:
                del states[key]
        else:
            window = states.get(key, [])
            window += [(ts, value)]
            # Trim window according to policy
            if cfg.window_type == WT_MEASURES:
                # Leave fixed amount of measures
                window = window[-cfg.window:]
                window_full = len(window) == cfg.window
            elif cfg.window_type == WT_TIME:
                # Time-based window
                window_full = ts - window[0][0] >= cfg.window
                while ts - window[0][0] > cfg.window:
                    window.pop(0)
            else:
                self.logger.error(
                    "Cannot calculate thresholds for %s (%s): Invalid window type '%s'",
                    m.metric, m.path, cfg.window_type
                )
                return None
            # Store back to context
            states[key] = window
        if not window_full:
            self.logger.error(
                "Cannot calculate thresholds for %s (%s): Window is not filled",
                m.metric, m.path
            )
            return None
        # Process window function
        wf = get_window_function(cfg.window_function)
        if not wf:
            self.logger.error(
                "Cannot calculate thresholds for %s (%s): Invalid window function %s",
                m.metric, m.path, cfg.window_function
            )
            return None
        try:
            return wf(window, cfg.window_config)
        except ValueError as e:
            self.logger.error(
                "Cannot calculate thresholds for %s (%s): %s",
                m.metric, m.path, e
            )
            return None

    def process_thresholds(self, m, cfg):
        """
        Check thresholds
        :param m: dict with metric result
        :param cfg: MetricConfig
        :return: List of umbrella alarm details
        """
        w_value = self.get_window_function(m, cfg)
        alarms = []
        if w_value is None:
            return alarms
        # Check thresholds
        path = m.metric
        if m.path:
            path += " | ".join(m.path)
        alarm_cfg = None
        if cfg.low_error is not None and w_value <= cfg.low_error:
            alarm_cfg = {
                "alarm_class": self.AC_PM_LOW_ERROR,
                "path": path,
                "severity": cfg.low_error_severity,
                "vars": {
                    "path": path,
                    "metric": m.metric,
                    "value": w_value,
                    "threshold": cfg.low_error,
                    "window_type": cfg.window_type,
                    "window": cfg.window,
                    "window_function": cfg.window_function
                }
            }
        elif cfg.low_warn is not None and w_value <= cfg.low_warn:
            alarm_cfg = {
                "alarm_class": self.AC_PM_LOW_WARN,
                "path": path,
                "severity": cfg.low_warn_severity,
                "vars": {
                    "path": path,
                    "metric": m.metric,
                    "value": w_value,
                    "threshold": cfg.low_warn,
                    "window_type": cfg.window_type,
                    "window": cfg.window,
                    "window_function": cfg.window_function
                }
            }
        elif cfg.high_error is not None and w_value >= cfg.high_error:
            alarm_cfg = {
                "alarm_class": self.AC_PM_HIGH_ERROR,
                "path": path,
                "severity": cfg.high_error_severity,
                "vars": {
                    "path": path,
                    "metric": m.metric,
                    "value": w_value,
                    "threshold": cfg.high_error,
                    "window_type": cfg.window_type,
                    "window": cfg.window,
                    "window_function": cfg.window_function
                }
            }
        elif cfg.high_warn is not None and w_value >= cfg.high_warn:
            alarm_cfg = {
                "alarm_class": self.AC_PM_HIGH_WARN,
                "path": path,
                "severity": cfg.high_warn_severity,
                "vars": {
                    "path": path,
                    "metric": m.metric,
                    "value": w_value,
                    "threshold": cfg.high_warn,
                    "window_type": cfg.window_type,
                    "window": cfg.window,
                    "window_function": cfg.window_function
                }
            }
        if alarm_cfg is not None:
            alarms += [alarm_cfg]
            # Apply umbrella filter handler
            if cfg.threshold_profile and cfg.threshold_profile.umbrella_filter_handler:
                try:
                    handler = get_handler(cfg.threshold_profile.umbrella_filter_handler)
                    if handler:
                        alarms = [handler(self, a) for a in alarms]
                        # Remove filtered alarms
                        alarms = [a for a in alarms if a]
                except Exception as e:
                    self.logger.error("Exception when loading handler %s", e)
        return alarms

    def send_metrics(self, data):
        """
        Convert collected metrics to Service.register_metric format
        :param data: (table fields, pk) -> field -> value
        :return:
        """
        # Normalized data
        # fields -> records
        chains = defaultdict(list)
        # Normalize data
        for (fields, pk), values in six.iteritems(data):
            # Sorted list of fields
            f = sorted(values)
            record_fields = "%s.%s" % (fields, ".".join(f))
            if isinstance(record_fields, unicode):
                record_fields = record_fields.encode("utf-8")
            record = "%s\t%s" % (pk, "\t".join(str(values[fn]) for fn in f))
            if isinstance(record, unicode):
                record = record.encode("utf-8")
            chains[record_fields] += [
                record
            ]
        # Spool data
        for f in chains:
            self.service.register_metrics(f, chains[f])
