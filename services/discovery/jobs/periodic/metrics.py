# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Metric collector
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import RLock
import datetime
from collections import defaultdict
import operator
# Third-party modules
import cachetools
from pymongo import ReadPreference
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.interface import Interface
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.pm.models.metrictype import MetricType
from noc.sla.models.slaprofile import SLAProfile
from noc.sla.models.slaprobe import SLAProbe


MAX31 = 0x7FFFFFFFL
MAX32 = 0xFFFFFFFFL
MAX64 = 0xFFFFFFFFFFFFFFFFL

NS = 1000000000.0

DEFAULT_THRESHOLDS = [None, None, None, None]


metrics_lock = RLock()


class MetricsCheck(DiscoveryCheck):
    """
    MAC discovery
    """
    name = "metrics"
    required_script = "get_metrics"

    _profile_metrics = cachetools.TTLCache(1000, 60)
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

    AC_PM_THRESHOLDS = AlarmClass.objects.get(name="NOC | PM | Out of Thresholds")

    SLA_CAPS = ["Cisco | IP | SLA | Probes"]

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_profile_metrics"), lock=lambda _: metrics_lock)
    def get_interface_profile_metrics(cls, p_id):
        r = {}
        ipr = InterfaceProfile.get_by_id(id=p_id)
        if not ipr:
            return r
        for m in ipr.metrics:
            if not m.is_active or m.metric_type.scope != "i":
                continue
            r[m.metric_type.name] = [
                m.low_error,
                m.low_warn,
                m.high_warn,
                m.high_error
            ]
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
            r[m.metric_type.name] = [
                m.low_error,
                m.low_warn,
                m.high_warn,
                m.high_error
            ]
        return r

    def handler(self):
        def q(s):
            return s.replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")

        def q_tags(t):
            return ",".join("%s=%s" % (q(s), q(t[s])) for s in sorted(t))

        self.logger.info("Collecting metrics")
        # Get interface configurations
        hints = {
            "ifindexes": {},
            "probes": {}
        }
        # <metric type name> -> {interfaces: [....], scope}
        metrics = {}
        # <metric type name> -> <interface name> -> thresholds
        i_thresholds = defaultdict(dict)
        # <metric type name> -> thresholds
        o_thresholds = defaultdict(dict)
        # Get objects metrics
        o_metrics = self.object.object_profile.metrics or []
        for m in o_metrics:
            mt_id = m.get("metric_type")
            if not mt_id:
                continue
            mt = MetricType.get_by_id(mt_id)
            if not mt:
                continue
            metrics[mt.name] = {
                "scope": "o"
            }
            le = m.get("low_error")
            lw = m.get("low_warn")
            he = m.get("high_error")
            hw = m.get("high_warn")
            o_thresholds[mt.name] = [
                int(le) if le is not None else None,
                int(lw) if lw is not None else None,
                int(he) if he is not None else None,
                int(hw) if hw is not None else None
            ]
        # Get interface metrics
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
                i_thresholds[metric][i["name"]] = ipr[metric]
        # Get SLA metrics
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
                hints["probes"][p.name] = {
                    "tests": [{
                        "name": t.name,
                        "type": t.type
                    } for t in p.tests]
                }
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
            key = "%s,%s" % (q(m["name"]), q_tags(m["tags"]))
            m["key"] = key
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
            batch += [
                "%s value=%s %s" % (
                    key,
                    m["abs_value"],
                    m["ts"] // 1000000000
                )
            ]
        # Send metrics
        if batch:
            self.logger.info("Spooling %d metrics", len(batch))
            self.service.register_metrics(batch)
        else:
            self.logger.info("No metrics to spool")
            return
        # Calculate max triggered threshold level
        oot = []
        oot_level = self.S_OK
        for m in result:
            if "abs_value" not in m:
                continue
            if m["name"] in o_thresholds:
                thresholds = o_thresholds[m["name"]]
            else:
                thresholds = i_thresholds.get(
                    m["name"], {}
                ).get(
                    m["tags"].get("interface"), DEFAULT_THRESHOLDS
                )
            if thresholds == DEFAULT_THRESHOLDS:
                continue
            v, condition, threshold = self.check_thresholds(m, thresholds)
            self.logger.debug(
                "Checking thresholds for %s@%s %s. measure=%s Result: %s",
                m["name"], m["tags"].get("interface"), thresholds,
                m["abs_value"], self.SMAP[v]
            )
            if v != self.S_OK:
                oot_level = max(oot_level, v)
                oot += [{
                    "name": m["name"],
                    "interface": m["tags"].get("interface"),
                    "value": m["value"],
                    "level": self.SMAP[v],
                    "condition": condition,
                    "threshold": threshold
                }]
        # Change status of existing alarm
        alarm = ActiveAlarm.objects.filter(
            managed_object=self.object.id,
            alarm_class=self.AC_PM_THRESHOLDS
        ).first()
        if oot_level == self.S_OK and alarm:
            # Clear alarm
            self.logger.info("Metrics are OK. Clearing alarm %s", alarm.id)
            alarm.clear_alarm("All metrics are back in thresholds range")
        elif oot_level != self.S_OK and not alarm:
            # Raise alarm
            alarm = ActiveAlarm(
                timestamp=datetime.datetime.now(),
                managed_object=self.object.id,
                alarm_class=self.AC_PM_THRESHOLDS,
                severity=self.SEV_MAP[oot_level],
                vars={
                    "thresholds": oot
                }
            )
            alarm.save()
            self.logger.info("Raising alarm %s with severity %s",
                             alarm.id, alarm.severity)
        elif oot_level != self.S_OK and alarm:
            s = self.SEV_MAP[oot_level]
            if s != alarm.severity:
                self.logger.info(
                    "Changing severity of alarm %s: %s -> %s",
                    alarm.id,
                    alarm.severity, s
                )
                alarm.change_severity(severity=s)
            self.logger.info("Updating alarm %s", alarm.id)
            v = alarm.vars
            v.update({
                "thresholds": oot
            })
            alarm.vars = v
            alarm.save()

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
