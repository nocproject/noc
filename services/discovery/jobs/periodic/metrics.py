# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Metric collector
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import threading
import datetime
from collections import defaultdict
## Third-party modules
import cachetools
## NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.interface import Interface
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmclass import AlarmClass


MAX31 = 0x7FFFFFFFL
MAX32 = 0xFFFFFFFFL
MAX64 = 0xFFFFFFFFFFFFFFFFL

NS = 1000000000.0

DEFAULT_THRESHOLDS = [None, None, None, None]


def get_interface_profile_metrics(p_id):
    with interface_profile_metrics_lock:
        r = {}
        ipr = InterfaceProfile.objects.filter(id=p_id).first()
        if not ipr:
            return None
        for m in ipr.metrics:
            if not m.is_active:
                continue
            r[m.metric_type.name] = [
                m.low_error,
                m.low_warn,
                m.high_warn,
                m.high_error
            ]
        return r

interface_profile_metrics_lock = threading.Lock()


class MetricsCheck(DiscoveryCheck):
    """
    MAC discovery
    """
    name = "metrics"
    required_script = "get_metrics"

    interface_profile_metrics_cache = cachetools.TTLCache(
        1000, 60, missing=get_interface_profile_metrics
    )
    # Last counter values
    counter_values = {}
    counter_lock = threading.Lock()

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

    def handler(self):
        def q(s):
            return s.replace(" ", "\\ ").replace(",", "\\,")

        def q_tags(t):
            return ",".join("%s=%s" % (q(s), q(t[s])) for s in sorted(t))

        self.logger.info("Collecting metrics")
        # Get interface configurations
        hints = {
            "ifindexes": {}
        }
        # <metric type name> -> {interfaces: [....], scope}
        metrics = {}
        # <metric type name> -> <interface name> -> thresholds
        i_thresholds = defaultdict(dict)
        for i in Interface._get_collection().find({
            "managed_object": self.object.id,
            "type": "physical"
        }, {
            "name": 1,
            "ifindex": 1,
            "profile": 1
        }):
            ipr = self.interface_profile_metrics_cache[i["profile"]]
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
        with self.counter_lock:
            for m in result:
                key = "%s,%s" % (q(m["name"]), q_tags(m["tags"]))
                m["key"] = key
                if m["type"] == "counter":
                    # Resolve counter
                    r = self.counter_values.get(key)
                    # Store value
                    self.counter_values[key] = (m["ts"], m["value"])
                    if r:
                        # Calculate counter
                        m["value"] = self.convert_counter(
                            m["ts"], m["value"],
                            r[0], r[1]
                        )
                        self.logger.debug(
                            "[%s] Old value: %s@%s, new value: %s@%s.",
                            key, r[1], r[0], m["value"], m["ts"]
                        )
                    else:
                        self.logger.debug(
                            "[%s] COUNTER value is not found. "
                            "Storing and waiting for a new result",
                            key
                        )
                        continue  # Skip the step
                self.logger.debug(
                    "[%s] Measured value: %s. Scale: %s. Resuling value: %s",
                    key, m["value"], m["scale"], m["value"] * m["scale"]
                )
                batch += [
                    "%s value=%s %s" % (
                        key,
                        m["value"] * m["scale"],
                        m["ts"]
                    )
                ]
        # Send metrics
        if batch:
            self.logger.debug("Spooling %d metrics", len(batch))
            self.job.scheduler.service.register_metrics("\n".join(batch))
        else:
            self.logger.debug("No metrics to spool")
        # Calculate max triggered threshold level
        oot = []
        oot_level = self.S_OK
        for m in result:
            thresholds = i_thresholds.get(
                m["name"], {}
            ).get(
                m["tags"].get("interface"), DEFAULT_THRESHOLDS
            )
            v = self.check_thresholds(m, thresholds)
            self.logger.debug(
                "Checking thresholds. %s@%s %s. Result: %s",
                m["name"], m["tags"].get("interface"), thresholds,
                self.SMAP[v]
            )
            if v != self.S_OK:
                oot_level = max(oot_level, v)
                oot += [{
                    "name": m["name"],
                    "interface": m["tags"].get("interface"),
                    "value": m["value"],
                    "level": self.SMAP[v]
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
                return old_value
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
        value = v["value"]
        low_error, low_warn, high_warn, high_error = thresholds
        if low_error is not None and value < low_error:
            return cls.S_ERROR
        if low_warn is not None and value < low_warn:
            return cls.S_WARN
        if high_error is not None and value > high_error:
            return cls.S_ERROR
        if high_warn is not None and value > high_warn:
            return cls.S_WARN
        return cls.S_OK
