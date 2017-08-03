# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Metric collector
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from collections import defaultdict
import operator
from collections import namedtuple
# Third-party modules
import cachetools
from pymongo import ReadPreference
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.interface import Interface
from noc.pm.models.metrictype import MetricType
from noc.sla.models.slaprofile import SLAProfile
from noc.sla.models.slaprobe import SLAProbe
from noc.core.handler import get_handler
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmseverity import AlarmSeverity


MAX31 = 0x7FFFFFFF
MAX32 = 0xFFFFFFFF
MAX64 = 0xFFFFFFFFFFFFFFFF

NS = 1000000000.0

metrics_lock = Lock()

MetricConfig = namedtuple("MetricConfig", [
    "is_stored",
    "window_type", "window", "window_function", "window_config",
    "window_related",
    "low_error", "low_warn", "high_warn", "high_error",
    "low_error_severity", "low_warn_severity", "high_warn_severity", "high_error_severity",
    "process_thresholds"
])


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

    SLA_CAPS = ["Cisco | IP | SLA | Probes"]

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
            if not m.get("is_active") or mt.scope != "o":
                continue
            le = m.get("low_error")
            lw = m.get("low_warn")
            he = m.get("high_error")
            hw = m.get("high_warn")
            lew = AlarmSeverity.severity_for_weight(int(m.get("low_error_weight", 10)))
            lww = AlarmSeverity.severity_for_weight(int(m.get("low_warn_weight", 1)))
            hew = AlarmSeverity.severity_for_weight(int(m.get("high_error_weight", 1)))
            hww = AlarmSeverity.severity_for_weight(int(m.get("high_warn_weight", 10)))
            r[mt.name] = MetricConfig(
                m.get("is_stored", True),
                m.get("window_type", "m"),
                int(m.get("window", 1)),
                m.get("window_function", "last"),
                m.get("window_config"),
                m.get("window_related", False),
                int(le) if le is not None else None,
                int(lw) if lw is not None else None,
                int(he) if he is not None else None,
                int(hw) if hw is not None else None,
                lew, lww, hew, hww,
                le is not None or lw is not None or he is not None or hw is not None
            )
        return r

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
            if not m.is_active or m.metric_type.scope != "i":
                continue
            r[m.metric_type.name] = MetricConfig(
                m.is_stored,
                m.window_type, m.window, m.window_function,
                m.window_config, m.window_related,
                m.low_error, m.low_warn, m.high_warn, m.high_error,
                AlarmSeverity.severity_for_weight(m.low_error_weight),
                AlarmSeverity.severity_for_weight(m.low_warn_weight),
                AlarmSeverity.severity_for_weight(m.high_warn_weight),
                AlarmSeverity.severity_for_weight(m.high_error_weight),
                m.low_error is not None or m.low_warn is not None or m.high_warn is not None or m.high_error is not None
            )
        return r

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_slaprofile_metrics"), lock=lambda _: metrics_lock)
    def get_slaprofile_metrics(cls, p_id):
        r = {}
        spr = SLAProfile.get_by_id(p_id)
        if not spr:
            return r
        for m in spr.metrics:
            if not m.is_active or m.metric_type.scope != "p":
                continue
            r[m.metric_type.name] = MetricConfig(
                m.is_stored,
                m.window_type, m.window, m.window_function,
                m.window_config, m.window_related,
                m.low_error, m.low_warn, m.high_warn, m.high_error,
                AlarmSeverity.severity_for_weight(m.low_error_weight),
                AlarmSeverity.severity_for_weight(m.low_warn_weight),
                AlarmSeverity.severity_for_weight(m.high_warn_weight),
                AlarmSeverity.severity_for_weight(m.high_error_weight),
                m.low_error is not None or m.low_warn is not None or m.high_warn is not None or m.high_error is not None
            )
        return r

    def handler(self):
        def q(ss):
            return ss.replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")

        def q_tags(tt):
            return ",".join("%s=%s" % (q(ss), q(tt[ss])) for ss in sorted(tt))

        self.logger.info("Collecting metrics")
        # Thresholds alarms
        alarms = []
        # Get interface configurations
        hints = {
            "ifindexes": {},
            "probes": {}
        }
        # <metric type name> -> {interfaces: [....], scope}
        metrics = {}
        # Get objects metrics
        # metric type -> MetricConfig
        o_metrics = self.get_object_profile_metrics(self.object.object_profile.id)
        self.logger.debug("Object metrics: %s", o_metrics)
        for m in o_metrics:
            metrics[m] = {
                "scope": "o"
            }
        # Get interface metrics
        # metric_type -> interface -> MetricConfig
        i_metrics = defaultdict(dict)
        for i in Interface._get_collection().find({
            "managed_object": self.object.id,
            "type": "physical"
        }, {
            "name": 1,
            "ifindex": 1,
            "profile": 1
        }, read_preference=ReadPreference.SECONDARY_PREFERRED):
            ipr = self.get_interface_profile_metrics(i["profile"])
            self.logger.debug("Interface %s. ipr=%s", i["name"], ipr)
            if not ipr:
                continue
            if "ifindex" in i:
                hints["ifindexes"][i["name"]] = i["ifindex"]
            for metric in ipr:
                if metric in metrics:
                    metrics[metric]["interfaces"] += [i["name"]]
                else:
                    metrics[metric] = {
                        "interfaces": [i["name"]],
                        "scope": "i"
                    }
                i_metrics[metric][i["name"]] = ipr[metric]
        # Get SLA metrics
        s_metrics = defaultdict(dict)
        if self.has_any_capability(self.SLA_CAPS):
            for p in SLAProbe.objects.filter(managed_object=self.object.id):
                if not p.profile:
                    self.logger.debug("Probe %s has no profile. Skipping", p.name)
                    continue
                pm = self.get_slaprofile_metrics(p.profile.id)
                if not pm:
                    self.logger.debug(
                        "Probe %s has profile '%s' with no configured metrics. "
                        "Skipping", p.name, p.profile.name
                    )
                    continue
                for metric in pm:
                    if metric in metrics:
                        metrics[metric]["probes"] += [p.name]
                    else:
                        metrics[metric] = {
                            "probes": [p.name],
                            "scope": "p"
                        }
                    s_metrics[metric][p.name] = pm[metric]
                hints["probes"][p.name] = {
                    "tests": [{
                        "name": t.name,
                        "type": t.type
                    } for t in p.tests]
                }
        else:
            self.logger.info("SLA not configured, skipping SLA metrics")
        # Collect metrics
        self.logger.debug("Collecting metrics: %s hints: %s",
                          metrics, hints)
        result = self.object.scripts.get_metrics(
            metrics=metrics,
            hints=hints
        )
        if not result:
            self.logger.info("No metrics found")
            return
        # Build output batch
        batch = []
        counters = self.job.context["counters"]
        for m in result:
            # Bind to config
            if m["name"] in o_metrics:
                cfg = o_metrics[m["name"]]
            elif m["name"] in i_metrics:
                cfg = i_metrics[m["name"]][m["tags"]["interface"]]
            elif m["name"] in s_metrics:
                cfg = s_metrics[m["name"]][m["tags"]["probe"]]
            else:
                self.logger.error("Ignoring metric %s: Cannot bind configuration", m["name"])
                continue
            key = "%s,%s" % (q(m["name"]), q_tags(m["tags"]))
            m["key"] = key
            # Process counters
            if m["type"] == "counter":
                # Resolve counter
                if self.job.reboot_detected:
                    # Drop previous counters on reboot
                    r = None
                    self.logger.info(
                        "[%s] Resetting counters due to device reboot",
                        key
                    )
                else:
                    # Get previous value
                    r = counters.get(key)
                # Store value
                counters[key] = (m["ts"], m["value"])
                if r:
                    self.logger.debug(
                        "[%s] Old value: %s@%s, new value: %s@%s.",
                        key, r[1], r[0], m["value"], m["ts"]
                    )
                    # Calculate counter
                    cv = self.convert_counter(
                        m["ts"], m["value"],
                        r[0], r[1]
                    )
                    if cv is None:
                        # Counter stepback or other errors
                        # Remove broken value
                        del counters[key]
                        continue
                    m["value"] = cv
                else:
                    self.logger.debug(
                        "[%s] COUNTER value is not found. "
                        "Storing and waiting for a new result",
                        key
                    )
                    continue  # Skip the step
            if m["type"] == "bool":
                m["abs_value"] = "true" if m["value"] else "false"
            else:
                m["abs_value"] = m["value"] * m["scale"]
            self.logger.debug(
                "[%s] Measured value: %s. Scale: %s. Resuling value: %s",
                key, m["value"], m["scale"], m["abs_value"]
            )
            # Schedule batch
            if cfg.is_stored:
                batch += [
                    "%s value=%s %s" % (
                        key,
                        m["abs_value"],
                        m["ts"] // 1000000000
                    )
                ]
            if cfg.process_thresholds and m["abs_value"]:
                alarms += self.process_thresholds(m, cfg)
        # Send metrics
        if batch:
            self.logger.info("Spooling %d metrics", len(batch))
            self.service.register_metrics(batch)
        else:
            self.logger.info("No metrics to spool")
        # Set up threshold alarms
        self.job.update_umbrella(
            self.AC_PM_THRESHOLDS,
            alarms
        )

    def convert_counter(self, new_ts, new_value, old_ts, old_value):
        """
        Calculate value from counter, gently handling overflows
        """
        dt = (float(new_ts) - float(old_ts)) / NS
        if new_value < old_value:
            # Counter decreased, either due wrap or stepback
            if old_value <= MAX31:
                mc = MAX31
            elif old_value <= MAX32:
                mc = MAX32
            else:
                mc = MAX64
            # Direct distance
            d_direct = old_value - new_value
            # Wrap distance
            d_wrap = new_value + (mc - old_value)
            if d_direct < d_wrap:
                # Possible counter stepback, return old_value
                self.logger.debug(
                    "Counter stepback: %s -> %s",
                    old_value, new_value
                )
                return None
            else:
                # Counter wrap
                self.logger.debug(
                    "Counter wrap: %s -> %s",
                    old_value, new_value
                )
                return float(d_wrap) / dt
        else:
            return (float(new_value) - float(old_value)) / dt

    @classmethod
    def check_thresholds(cls, v, thresholds):
        value = v["abs_value"]
        low_error, low_warn, high_warn, high_error = thresholds
        if low_error is not None and value < low_error:
            return cls.S_ERROR, "<", low_error
        if low_warn is not None and value < low_warn:
            return cls.S_WARN, "<", low_warn
        if high_error is not None and value > high_error:
            return cls.S_ERROR, ">", high_error
        if high_warn is not None and value > high_warn:
            return cls.S_WARN, ">", high_warn
        return cls.S_OK, None, None

    def process_thresholds(self, m, cfg):
        """
        Check thresholds
        :param m: dict with metric result
        :param cfg: MetricConfig
        :return: List of umbrella alarm details
        """
        states = self.job.context["metric_windows"]
        #
        alarms = []
        if not w_value:
            return alarms
        value = m["abs_value"]
        ts = m["ts"] // 1000000000
        # Do not store single-value windows
        drop_window = cfg.window_type == "m" and cfg.window == 1
        # Restore window
        if drop_window:
            window = [(ts, value)]
            window_full = True
            if m["key"] in states:
                del states[m["key"]]
        else:
            window = states.get(m["key"], [])
            window += [(ts, value)]
            # Trim window according to policy
            if cfg.window_type == m:
                # Leave fixed amount of measures
                window = window[-cfg.window:]
                window_full = len(window) == cfg.window
            elif cfg.window_type == "t":
                # Time-based window
                window_full = ts - window[0][0] >= cfg.window
                while ts - window[0][0] > cfg.window:
                    window.pop(0)
            else:
                self.logger.error(
                    "Cannot calculate thresholds for %s (%s): Invalid window type '%s'",
                    m["name"], m["tags"], cfg.window_type
                )
                return alarms
            # Store back to context
            states[m["key"]] = window
        if not window_full:
            self.logger.error(
                "Cannot calculate thresholds for %s (%s): Window is not filled",
                m["name"], m["tags"]
            )
            return alarms
        # Process window function
        wf = getattr(self, "wf_%s" % cfg.window_function, None)
        if not wf:
            self.logger.error(
                "Cannot calculate thresholds for %s (%s): Invalid window function %s",
                m["name"], m["tags"], cfg.window_function
            )
            return alarms
        try:
            w_value = wf(window, cfg.window_config)
        except ValueError as e:
            self.logger.error(
                "Cannot calculate thresholds for %s (%s): %s",
                m["name"], m["tags"], e
            )
            return alarms
        # Check thresholds
        path = m["name"]
        if "interface" in m["tags"]:
            scope = m["tags"]["interface"]
        elif "probe" in m["tags"]:
            scope = m["tags"]["probe"]
        else:
            scope = ""
        if scope:
            path += " | %s" % scope
        if cfg.low_error is not None and w_value <= cfg.low_error:
            alarms += [{
                "alarm_class": self.AC_PM_LOW_ERROR,
                "path": path,
                "severity": cfg.low_error_severity,
                "vars": {
                    "path": path,
                    "metric": m["name"],
                    "scope": scope,
                    "value": w_value,
                    "threshold": cfg.low_error,
                    "window_type": cfg.window_type,
                    "window": cfg.window,
                    "window_function": cfg.window_function
                }
            }]
        elif cfg.low_warn is not None and w_value <= cfg.low_warn:
            alarms += [{
                "alarm_class": self.AC_PM_LOW_WARN,
                "path": path,
                "severity": cfg.low_warn_severity,
                "vars": {
                    "path": path,
                    "metric": m["name"],
                    "scope": scope,
                    "value": w_value,
                    "threshold": cfg.low_warn,
                    "window_type": cfg.window_type,
                    "window": cfg.window,
                    "window_function": cfg.window_function
                }
            }]
        elif cfg.high_error is not None and w_value >= cfg.high_error:
            alarms += [{
                "alarm_class": self.AC_PM_HIGH_ERROR,
                "path": path,
                "severity": cfg.high_error_severity,
                "vars": {
                    "path": path,
                    "metric": m["name"],
                    "scope": scope,
                    "value": w_value,
                    "threshold": cfg.high_error,
                    "window_type": cfg.window_type,
                    "window": cfg.window,
                    "window_function": cfg.window_function
                }
            }]
        elif cfg.high_warn is not None and w_value >= cfg.high_warn:
            alarms += [{
                "alarm_class": self.AC_PM_HIGH_WARN,
                "path": path,
                "severity": cfg.high_warn_severity,
                "vars": {
                    "path": path,
                    "metric": m["name"],
                    "scope": scope,
                    "value": w_value,
                    "threshold": cfg.high_warn,
                    "window_type": cfg.window_type,
                    "window": cfg.window,
                    "window_function": cfg.window_function
                }
            }]
        return alarms

    def wf_last(self, window, *args, **kwargs):
        """
        Returns last measured value
        :param window:
        :return:
        """
        return window[-1][1]

    def wf_avg(self, window, *args, **kwargs):
        """
        Returns window average
        :param window:
        :return:
        """
        return float(sum(w[1] for w in window)) / len(window)

    def _wf_percentile(self, window, q):
        """
        Calculate percentile
        :param window:
        :param q:
        :return:
        """
        l = sorted(w[1] for w in window)
        i = len(l) * q // 100
        return l[i]

    def wf_percentile(self, window, config, *args, **kwargs):
        """
        Calculate percentile
        :param window:
        :param config:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            q = int(config)
        except ValueError:
            raise ValueError("Percentile must be integer")
        if q < 0 or q > 100:
            raise ValueError("Percentile must be >0 and <100")
        return self._wf_percentile(window, q)

    def wf_q1(self, window, *args, **kwargs):
        """
        1st quartile
        :param window:
        :param args:
        :param kwargs:
        :return:
        """
        return self._wf_percentile(window, 25)

    def wf_q2(self, window, *args, **kwargs):
        """
        1st quartile
        :param window:
        :param args:
        :param kwargs:
        :return:
        """
        return self._wf_percentile(window, 50)

    def wf_q3(self, window, *args, **kwargs):
        """
        1st quartile
        :param window:
        :param args:
        :param kwargs:
        :return:
        """
        return self._wf_percentile(window, 75)

    def wf_p95(self, window, *args, **kwargs):
        """
        1st quartile
        :param window:
        :param args:
        :param kwargs:
        :return:
        """
        return self._wf_percentile(window, 95)

    def wf_p99(self, window, *args, **kwargs):
        """
        1st quartile
        :param window:
        :param args:
        :param kwargs:
        :return:
        """
        return self._wf_percentile(window, 99)

    def wf_handler(self, window, config, *args, **kwargs):
        """
        Calculate via handler
        :param window:
        :param config:
        :param args:
        :param kwargs:
        :return:
        """
        h = get_handler(config)
        if not h:
            raise ValueError("Invalid handler %s" % config)
        return h(window)
