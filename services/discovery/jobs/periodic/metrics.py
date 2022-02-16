# ---------------------------------------------------------------------
# Metric collector
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import itertools
import time
from collections import defaultdict
from typing import Any, Optional, List, Dict, Set, Tuple

# Third-party modules
import cachetools
from pymongo import ReadPreference
import orjson

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.models.problem import ProblemItem
from noc.inv.models.object import Object
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.interfaceprofile import InterfaceProfile, MetricConfig
from noc.inv.models.sensorprofile import SensorProfile
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.sensor import Sensor
from noc.fm.models.alarmclass import AlarmClass
from noc.pm.models.metrictype import MetricType
from noc.sla.models.slaprofile import SLAProfile
from noc.sla.models.slaprobe import SLAProbe
from noc.wf.models.state import State
from noc.pm.models.thresholdprofile import ThresholdConfig
from noc.core.hash import hash_str


MAX31 = 0x7FFFFFFF
MAX32 = 0xFFFFFFFF
MAX64 = 0xFFFFFFFFFFFFFFFF

NS = 1000000000.0

MT_COUNTER = "counter"
MT_BOOL = "bool"
MT_DELTA = "delta"
MT_COUNTER_DELTA = {MT_COUNTER, MT_DELTA}

WT_MEASURES = "m"
WT_TIME = "t"

SCOPE_OBJECT = "object"
SCOPE_INTERFACE = "interface"
SCOPE_SLA = "sla"

metrics_lock = Lock()


class MData(object):
    __slots__ = (
        "id",
        "ts",
        "metric",
        "labels",
        "value",
        "scale",
        "type",
        "abs_value",
        "label",
        "_key_fmt",
    )

    def __init__(
        self,
        id,
        ts,
        metric,
        labels=None,
        value=None,
        scale=None,
        type=None,
        abs_value=None,
    ):
        self.id = id
        self.ts = ts
        self.metric = metric
        self.labels = labels
        self.value = value
        self.scale = scale
        self.type = type
        self.abs_value = abs_value
        if labels:
            self.label = "%s|%s" % (metric, "|".join(str(label) for label in sorted(labels)))
            self._key_fmt = "%%x|%s" % ("|".join(str(label) for label in sorted(labels)),)
        else:
            self.label = metric
            self._key_fmt = "%x"

    def __repr__(self):
        return f"<MData #{self.id} {self.metric}>"

    def get_key(self, x: int) -> str:
        return self._key_fmt % x


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

    SMAP = {0: "ok", 1: "warn", 2: "error"}

    SEV_MAP = {1: 2000, 2: 3000}

    SLA_CAPS = ["Cisco | IP | SLA | Probes"]

    umbrella_cls = "NOC | PM | Out of Thresholds"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_count = itertools.count()
        self.id_metrics: Dict[str, MetricConfig] = {}
        self.id_ctx: Dict[str, Dict[str, Any]] = {}
        # MetricID -> SensorId Map
        self.sensors_metrics: Dict[str, int] = {}
        # MetricID -> SLAId Map
        self.sla_probe_metrics: Dict[str, int] = {}

    @staticmethod
    @cachetools.cached({})
    def get_ac_pm_thresholds():
        return AlarmClass.get_by_name("NOC | PM | Out of Thresholds")

    def get_object_metrics(self) -> List[Dict[str, Any]]:
        """
        Populate metrics list with objects metrics
        :return:
        """
        # @todo: Inject ManagedObject.effective_labels
        metrics = []
        o_metrics = ManagedObjectProfile.get_object_profile_metrics(self.object.object_profile.id)
        self.logger.debug("Object metrics: %s", o_metrics)
        for metric in o_metrics:
            if (self.is_box and not o_metrics[metric].enable_box) or (
                self.is_periodic and not o_metrics[metric].enable_periodic
            ):
                continue
            m_id = next(self.id_count)
            metrics += [{"id": m_id, "metric": metric}]
            self.id_metrics[m_id] = o_metrics[metric]
        if not metrics:
            self.logger.info("Object metrics are not configured. Skipping")
        return metrics

    def get_subinterfaces(self):
        subs = defaultdict(list)  # interface id -> [{"name":, "ifindex":}]
        for si in (
            SubInterface._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .find({"managed_object": self.object.id}, {"name": 1, "interface": 1, "ifindex": 1})
        ):
            subs[si["interface"]] += [{"name": si["name"], "ifindex": si.get("ifindex")}]
        return subs

    def get_interface_metrics(self) -> List[Dict[str, Any]]:
        """
        Populate metrics list with interface metrics
        :return:
        """
        # @todo: Inject Interface.effective_labels
        subs = None
        metrics = []
        for i in (
            Interface._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .find(
                {"managed_object": self.object.id, "type": "physical"},
                {
                    "_id": 1,
                    "name": 1,
                    "ifindex": 1,
                    "profile": 1,
                    "in_speed": 1,
                    "out_speed": 1,
                    "bandwidth": 1,
                },
            )
        ):
            ipr = InterfaceProfile.get_interface_profile_metrics(i["profile"])
            self.logger.debug("Interface %s. ipr=%s", i["name"], ipr)
            if not ipr:
                continue  # No metrics configured
            i_profile = InterfaceProfile.get_by_id(i["profile"])
            if i_profile.allow_subinterface_metrics and subs is None:
                # Resolve subinterfaces
                subs = self.get_subinterfaces()
            ifindex = i.get("ifindex")
            for metric in ipr:
                if (self.is_box and not ipr[metric].enable_box) or (
                    self.is_periodic and not ipr[metric].enable_periodic
                ):
                    continue
                m_id = next(self.id_count)
                m = {"id": m_id, "metric": metric, "labels": [f"noc::interface::{i['name']}"]}
                if ifindex is not None:
                    m["ifindex"] = ifindex
                metrics += [m]
                self.id_metrics[m_id] = ipr[metric]
                if i_profile.allow_subinterface_metrics:
                    for si in subs[i["_id"]]:
                        if si["name"] != i["name"]:
                            m_id = next(self.id_count)
                            m = {
                                "id": m_id,
                                "metric": metric,
                                "labels": [
                                    f"noc::interface::{i['name']}",
                                    f"noc::subinterface::{si['name']}",
                                ],
                            }
                            if si["ifindex"] is not None:
                                m["ifindex"] = si["ifindex"]
                            metrics += [m]
                            self.id_metrics[m_id] = ipr[metric]
                threshold_profile = ipr[metric].threshold_profile
                if threshold_profile and threshold_profile.value_handler:
                    # Fill window context
                    in_speed: int = i.get("in_speed") or 0
                    out_speed: int = i.get("out_speed") or 0
                    bandwidth: int = i.get("bandwidth") or 0
                    if in_speed and not out_speed:
                        out_speed = in_speed
                    elif not in_speed and out_speed:
                        in_speed = out_speed
                    if not bandwidth:
                        bandwidth = max(in_speed, out_speed)
                    self.id_ctx[m_id] = {
                        "in_speed": in_speed,
                        "out_speed": out_speed,
                        "bandwidth": bandwidth,
                    }
        if not metrics:
            self.logger.info("Interface metrics are not configured. Skipping")
        return metrics

    def get_sla_metrics(self) -> List[Dict[str, Any]]:
        if not self.has_any_capability(self.SLA_CAPS):
            self.logger.info("SLA not configured, skipping SLA metrics")
        metrics = []
        for p in (
            SLAProbe._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .find(
                {"managed_object": self.object.id},
                {"name": 1, "state": 1, "group": 1, "profile": 1, "type": 1, "bi_id": 1},
            )
        ):
            if not p.get("profile"):
                self.logger.debug("Probe %s has no profile. Skipping", p["name"])
                continue
            state = State.get_by_id(p["state"])
            if not state.is_productive:
                self.logger.debug("[%s] SLA Probe is not productive state. Skipping", p["name"])
                continue
            pm = SLAProfile.get_slaprofile_metrics(p["profile"])
            if not pm:
                self.logger.debug(
                    "Probe %s has profile '%s' with no configured metrics. " "Skipping",
                    p["name"],
                    p["profile"],
                )
                continue
            for metric in pm:
                if (self.is_box and not pm[metric].enable_box) or (
                    self.is_periodic and not pm[metric].enable_periodic
                ):
                    continue
                m_id = next(self.id_count)
                labels = [f"noc::sla::name::{p['name']}"]
                sla_group = p.get("group", "")
                if sla_group:
                    labels += [f"noc::sla::group::{sla_group}"]
                metrics += [
                    {
                        "id": m_id,
                        "metric": metric,
                        "labels": labels,
                        "sla_type": p["type"],
                    }
                ]
                self.id_metrics[m_id] = pm[metric]
                self.sla_probe_metrics[m_id] = p["bi_id"]
        if not metrics:
            self.logger.info("SLA metrics are not configured. Skipping")
        return metrics

    def get_sensor_metrics(self) -> List[Dict[str, Any]]:
        metrics = []
        o = Object.get_managed(self.object).values_list("id")
        for s in (
            Sensor._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .find(
                {"object": {"$in": list(o)}, "snmp_oid": {"$exists": True}},
                {"local_id": 1, "profile": 1, "state": 1, "snmp_oid": 1, "labels": 1, "bi_id": 1},
            )
        ):
            if not s.get("profile"):
                self.logger.debug("[%s] Sensor has no profile. Skipping", s["local_id"])
                continue
            pm: "SensorProfile" = SensorProfile.get_by_id(s["profile"])
            if not pm.enable_collect:
                continue
            state = State.get_by_id(s["state"])
            if not state.is_productive:
                self.logger.debug("[%s] Sensor is not productive state. Skipping", s["local_id"])
                continue
            for mtype in ["Sensor | Value", "Sensor | Status"]:
                m_id = next(self.id_count)
                metric = MetricType.get_by_name(mtype)
                labels = [f'noc::sensor::{s["local_id"]}'] + s.get("labels", [])
                metrics += [
                    {
                        "id": m_id,
                        "metric": metric.name,
                        "labels": labels,
                        "oid": s["snmp_oid"],
                    }
                ]
                self.id_metrics[m_id] = MetricConfig(metric, False, True, True, None)
                self.sensors_metrics[m_id] = int(s["bi_id"])
        return metrics

    def process_result(
        self, result: List[MData]
    ) -> Tuple[int, Dict[str, Dict[str, Dict[str, Any]]], List[ProblemItem], List[Dict[str, Any]]]:
        """
        Process IGetMetrics result
        :param result:
        :return:
        """
        # Restore last counter state
        if self.has_artefact("reboot"):
            self.logger.info("Resetting counter context due to detected reboot")
            self.job.context["counters"] = {}
        counters = self.job.context["counters"]
        alarms = []
        events = []
        data = defaultdict(dict)  # table -> item hash -> {field:value, ...}
        n_metrics = 0
        mo_id = self.object.bi_id
        ts_cache = {}  # timestamp -> (date, ts)
        # Calculate time_delta
        time_delta = self.job.context.get("time_delta", None)
        if time_delta:
            del self.job.context["time_delta"]  # Remove from context
        if time_delta and time_delta > 0xFFFF:
            self.logger.info(
                "time_delta overflow (%d). time_delta measurement will be dropped" % time_delta
            )
            time_delta = None
        # Process collected metrics
        seen: Set[str] = set()
        for m in result:
            # Filter out duplicates
            labels = m.labels
            cfg = self.id_metrics.get(m.id)
            key = m.get_key(cfg.metric_type.bi_id)
            if key in seen:
                # Prevent duplicated metrics
                self.logger.error(
                    "Duplicated metric %s [%s]. Ignoring",
                    cfg.metric_type.name,
                    "|".join(str(label) for label in sorted(labels)),
                )
                continue
            seen.add(key)
            if m.type in MT_COUNTER_DELTA:
                # Counter type
                # Restore old value and save new
                r = counters.get(key)
                counters[key] = (m.ts, m.value)
                if r is None:
                    # No stored state
                    self.logger.debug(
                        "[%s] COUNTER value is not found. " "Storing and waiting for a new result",
                        m.label,
                    )
                    continue
                # Calculate counter
                self.logger.debug(
                    "[%s] Old value: %s@%s, new value: %s@%s.", m.label, r[1], r[0], m.value, m.ts
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
                        m.label,
                        r[1],
                        r[0],
                        m.value,
                        m.ts,
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
                m.label,
                m.value,
                m.scale,
                m.abs_value,
            )
            # Schedule to store
            if cfg.is_stored:
                tsc = ts_cache.get(m.ts)
                if not tsc:
                    lt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m.ts // 1000000000))
                    tsc = (lt.split(" ")[0], lt)
                    ts_cache[m.ts] = tsc
                if labels:
                    item_hash = hash_str(str((tsc[1], mo_id, labels)))
                else:
                    item_hash = hash_str(str((tsc[1], mo_id)))
                record = data[cfg.metric_type.scope.table_name].get(item_hash)
                if not record:
                    record = {"date": tsc[0], "ts": tsc[1], "managed_object": mo_id}
                    if labels:
                        record["labels"] = labels
                    if m.id in self.sensors_metrics:
                        record["sensor"] = self.sensors_metrics[m.id]
                    if m.id in self.sla_probe_metrics:
                        record["sla_probe"] = self.sla_probe_metrics[m.id]
                    data[cfg.metric_type.scope.table_name][item_hash] = record
                field = cfg.metric_type.field_name
                try:
                    record[field] = cfg.metric_type.clean_value(m.abs_value)
                except ValueError as e:
                    self.logger.info("[%s] Cannot clean value %s: %s", m.label, m.abs_value, e)
                    continue
                # Attach time_delta, when required
                if time_delta and cfg.metric_type.scope.enable_timedelta:
                    data[cfg.metric_type.scope.table_name][item_hash]["time_delta"] = time_delta
                n_metrics += 1
            # Metrics path
            path = m.metric
            if m.labels:
                m_path = " | ".join(sorted(m.labels))
                if not path.endswith(m_path):
                    path = "%s | %s" % (path, m_path)
            if cfg.threshold_profile and m.abs_value is not None:
                alarm, event = self.process_thresholds(m, cfg, path, labels)
                alarms += alarm
                events += event
            elif self.job.context["active_thresholds"].get(path):
                alarm, event = self.clear_process_thresholds(m, cfg, path, labels)
                alarms += alarm
                events += event
            else:
                # Build window state key
                key = m.get_key(cfg.metric_type.bi_id)
                if self.job.context["metric_windows"].get(key):
                    del self.job.context["metric_windows"][key]
        return n_metrics, data, alarms, events

    def handler(self):
        self.logger.info("Collecting metrics")
        # Build get_metrics input parameters
        metrics = self.get_object_metrics()
        metrics += self.get_interface_metrics()
        metrics += self.get_sla_metrics()
        metrics += self.get_sensor_metrics()
        if not metrics:
            self.logger.info("No metrics configured. Skipping")
            return
        # Collect metrics
        ts = time.time()
        if "last_run" in self.job.context and self.job.context["last_run"] < ts:
            self.job.context["time_delta"] = int(round(ts - self.job.context["last_run"]))
        self.job.context["last_run"] = ts
        self.logger.debug("Collecting metrics: %s", metrics)
        result = [MData(**r) for r in self.object.scripts.get_metrics(metrics=metrics)]
        if not result:
            self.logger.info("No metrics found")
            return
        # Process results
        n_metrics, data, alarms, events = self.process_result(result)
        # Send metrics
        if n_metrics:
            self.logger.info("Spooling %d metrics", n_metrics)
            for table in data:
                self.service.register_metrics(table, list(data[table].values()), key=self.object.id)
        # Set up threshold alarms
        self.logger.info("%d alarms detected", len(alarms))
        if events:
            self.logger.info("%d events detected", len(events))
        self.job.update_alarms(
            alarms,
            group_cls=self.umbrella_cls,
            group_reference=f"g:t:{self.object.id}:{self.umbrella_cls}",
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
                self.logger.debug("[%s] Counter stepback: %s -> %s", m.label, r[1], m.value)
                return None
            else:
                # Counter wrap
                self.logger.debug("[%s] Counter wrap: %s -> %s", m.label, r[1], m.value)
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

    def get_window_function(self, m: MData, cfg: MetricConfig) -> Optional[Any]:
        """
        Check thresholds
        :param m: dict with metric result
        :param cfg: MetricConfig
        :return: Value or None
        """
        # Build window state key
        key = m.get_key(cfg.metric_type.bi_id)
        #
        states = self.job.context["metric_windows"]
        value = m.abs_value
        if cfg.threshold_profile.value_handler:
            if cfg.threshold_profile.value_handler.allow_threshold_value_handler:
                vh = cfg.threshold_profile.value_handler.get_handler()
                if vh:
                    ctx = self.id_ctx.get(m.id) or {}
                    try:
                        value = vh(value, **ctx)
                    except Exception as e:
                        self.logger.error(
                            "Failed to execute value handler %s: %s",
                            cfg.threshold_profile.value_handler,
                            e,
                        )
            else:
                self.logger.warning("Value Handler is not allowed for Thresholds")
        ts = m.ts // 1000000000
        # Do not store single-value windows
        window_type = cfg.threshold_profile.window_type
        ws = cfg.threshold_profile.window
        drop_window = window_type == "m" and ws == 1
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
            if window_type == WT_MEASURES:
                # Leave fixed amount of measures
                window = window[-ws:]
                window_full = len(window) == ws
            elif window_type == WT_TIME:
                # Time-based window
                window_full = ts - window[0][0] >= ws >= ts - window[-2::][0][0]
                while ts - window[0][0] > ws:
                    window.pop(0)
            else:
                self.logger.error(
                    "Cannot calculate thresholds for %s (%s): Invalid window type '%s'",
                    m.metric,
                    m.labels,
                    window_type,
                )
                return None
            # Store back to context
            states[key] = window
        if not window_full:
            self.logger.error(
                "Cannot calculate thresholds for %s (%s): Window is not filled", m.metric, m.labels
            )
            return None
        # Process window function
        wf = cfg.threshold_profile.get_window_function()
        if not wf:
            self.logger.error(
                "Cannot calculate thresholds for %s (%s): Invalid window function %s",
                m.metric,
                m.labels,
                cfg.threshold_profile.window_function,
            )
            return None
        try:
            return wf(window, cfg.threshold_profile.window_config)
        except ValueError as e:
            self.logger.error("Cannot calculate thresholds for %s (%s): %s", m.metric, m.labels, e)
            return None

    def clear_process_thresholds(self, m, cfg, path, labels=None):
        """
        Check thresholds
        :param m: dict with metric result
        :param cfg: MetricConfig
        :param path:
        :param labels:
        :return: List of umbrella alarm details
        """
        alarms = []
        events = []
        key = m.get_key(cfg.metric_type.bi_id)
        #
        active = self.job.context["active_thresholds"].get(path)
        threshold_profile = active["threshold_profile"]
        threshold = threshold_profile.find_threshold(active["threshold"])
        if threshold:
            # Close Event
            self.logger.debug(
                "Remove active thresholds %s from metric %s",
                self.job.context["active_thresholds"].get(path),
                path,
            )
            del self.job.context["active_thresholds"][path]
            if self.job.context["metric_windows"].get(key):
                del self.job.context["metric_windows"][key]
            if threshold.close_event_class:
                events += self.get_event_cfg(
                    cfg,
                    threshold_profile,
                    threshold.name,
                    threshold.close_event_class.name,
                    path,
                    m.value,
                    labels=labels,
                    sensor=self.sensors_metrics.get(m.id),
                    sla_probe=self.sla_probe_metrics.get(m.id),
                )
            if threshold.close_handler:
                if threshold.close_handler.allow_threshold:
                    handler = threshold.close_handler.get_handler()
                    if handler:
                        try:
                            handler(self, cfg, threshold, m.value)
                        except Exception as e:
                            self.logger.error("Exception when calling close handler: %s", e)
                else:
                    self.logger.warning("Handler is not allowed for Thresholds")
        return alarms, events

    def process_thresholds(
        self, m: MData, cfg: MetricConfig, path: str, labels: Optional[List[str]] = None
    ):
        """
        Check thresholds
        :param m: dict with metric result
        :param cfg: MetricConfig
        :param path: Metric path
        :param labels: Metric labels
        :return: List of umbrella alarm details
        """
        alarms = []
        events = []
        new_threshold = None
        # Get active threshold name
        active = self.job.context["active_thresholds"].get(path)
        # Check if profile has configured thresholds
        if not cfg.threshold_profile.thresholds and not active:
            return alarms, events
        w_value = self.get_window_function(m, cfg)
        if w_value is None and not active:
            return alarms, events
        if w_value is None:
            w_value = m.abs_value
        if active:
            # Check we should close existing threshold
            for th in cfg.threshold_profile.thresholds:
                if th.is_open_match(w_value):
                    new_threshold = th
                    break
            threshold = cfg.threshold_profile.find_threshold(active["threshold"])
            if new_threshold and threshold != new_threshold:
                # Close Event
                active = None  # Reset threshold
                del self.job.context["active_thresholds"][path]
                if threshold.close_event_class:
                    events += self.get_event_cfg(
                        cfg,
                        cfg.threshold_profile,
                        threshold.name,
                        threshold.close_event_class.name,
                        path,
                        w_value,
                        labels=labels,
                        sensor=self.sensors_metrics.get(m.id),
                        sla_probe=self.sla_probe_metrics.get(m.id),
                    )
                if threshold.close_handler:
                    if threshold.close_handler.allow_threshold:
                        handler = threshold.close_handler.get_handler()
                        if handler:
                            try:
                                handler(self, cfg, threshold, w_value)
                            except Exception as e:
                                self.logger.error("Exception when calling close handler: %s", e)
                    else:
                        self.logger.warning("Handler is not allowed for Thresholds")
                elif threshold.alarm_class:
                    # Remain umbrella alarm
                    alarms += self.get_umbrella_alarm_cfg(
                        cfg,
                        threshold,
                        path,
                        w_value,
                        labels=labels,
                        sensor=self.sensors_metrics.get(m.id),
                        sla_probe=self.sla_probe_metrics.get(m.id),
                    )
            elif threshold:
                if threshold.is_clear_match(w_value):
                    # Close Event
                    active = None  # Reset threshold
                    del self.job.context["active_thresholds"][path]
                    if threshold.close_event_class:
                        events += self.get_event_cfg(
                            cfg,
                            cfg.threshold_profile,
                            threshold.name,
                            threshold.close_event_class.name,
                            path,
                            w_value,
                            labels=labels,
                            sensor=self.sensors_metrics.get(m.id),
                            sla_probe=self.sla_probe_metrics.get(m.id),
                        )
                    if threshold.close_handler:
                        if threshold.close_handler.allow_threshold:
                            handler = threshold.close_handler.get_handler()
                            if handler:
                                try:
                                    handler(self, cfg, threshold, w_value)
                                except Exception as e:
                                    self.logger.error("Exception when calling close handler: %s", e)
                        else:
                            self.logger.warning("Handler is not allowed for Thresholds")
                if threshold.alarm_class:
                    # Remain umbrella alarm
                    alarms += self.get_umbrella_alarm_cfg(
                        cfg,
                        threshold,
                        path,
                        w_value,
                        labels=labels,
                        sensor=self.sensors_metrics.get(m.id),
                        sla_probe=self.sla_probe_metrics.get(m.id),
                    )
            else:
                # Threshold has been reconfigured or deleted
                if active.get("close_event_class"):
                    events += self.get_event_cfg(
                        cfg,
                        active["threshold_profile"],
                        active["threshold"],
                        active["close_event_class"].name,
                        path,
                        w_value,
                        labels=labels,
                        sensor=self.sensors_metrics.get(m.id),
                        sla_probe=self.sla_probe_metrics.get(m.id),
                    )
                if active.get("close_handler"):
                    if active["close_handler"].allow_threshold:
                        handler = active["close_handler"].get_handler()
                        if handler:
                            try:
                                handler(self, cfg, active["threshold"], w_value)
                            except Exception as e:
                                self.logger.error("Exception when calling close handler: %s", e)
                    else:
                        self.logger.warning("Handler is not allowed for Thresholds")
                active = None
                del self.job.context["active_thresholds"][path]
        if not active:
            # Check opening thresholds only if no active threshold remains
            for threshold in cfg.threshold_profile.thresholds:
                if not threshold.is_open_match(w_value):
                    continue
                # Set context
                self.job.context["active_thresholds"][path] = {
                    "threshold": threshold.name,
                    "threshold_profile": cfg.threshold_profile,
                    "close_event_class": threshold.close_event_class,
                    "close_handler": threshold.close_handler,
                }
                if threshold.open_event_class:
                    # Raise Event
                    events += self.get_event_cfg(
                        cfg,
                        cfg.threshold_profile,
                        threshold.name,
                        threshold.open_event_class.name,
                        path,
                        w_value,
                        labels=labels,
                        sensor=self.sensors_metrics.get(m.id),
                        sla_probe=self.sla_probe_metrics.get(m.id),
                    )
                if threshold.open_handler:
                    if threshold.open_handler.allow_threshold:
                        # Call handler
                        handler = threshold.open_handler.get_handler()
                        if handler:
                            try:
                                handler(self, cfg, threshold, w_value)
                            except Exception as e:
                                self.logger.error("Exception when calling open handler: %s", e)
                    else:
                        self.logger.warning("Handler is not allowed for Thresholds")
                if threshold.alarm_class:
                    # Raise umbrella alarm
                    alarms += self.get_umbrella_alarm_cfg(
                        cfg,
                        threshold,
                        path,
                        w_value,
                        labels=labels,
                        sensor=self.sensors_metrics.get(m.id),
                        sla_probe=self.sla_probe_metrics.get(m.id),
                    )
                break
        return alarms, events

    def get_umbrella_alarm_cfg(
        self,
        metric_config: "MetricConfig",
        threshold: "ThresholdConfig",
        path: str,
        value: float,
        labels=None,
        sensor=None,
        sla_probe=None,
    ):
        """
        Get configuration for umbrella alarm
        :param threshold:
        :param path:
        :param metric_config:
        :param value:
        :param labels:
        :param sensor:
        :param sla_probe:
        :return: List of dicts or empty list
        """
        self.logger.debug("Get Umbrella Alarm CFG: %s", metric_config)
        alarm_cfg = {
            "alarm_class": threshold.alarm_class.name,
            "path": path,
            "vars": {
                "path": [path],
                "metric": metric_config.metric_type.name,
                "ovalue": value,
                "tvalue": threshold.value,
                "window_type": metric_config.threshold_profile.window_type,
                "window": metric_config.threshold_profile.window,
                "window_function": metric_config.threshold_profile.window_function,
            },
        }
        if sensor:
            alarm_cfg["vars"]["sensor"] = str(sensor)
        if sla_probe:
            alarm_cfg["vars"]["sla_probe"] = str(sla_probe)
        for ll in labels:
            scope, value = ll.rsplit("::", 1)
            if scope.startswith("noc::interface"):
                alarm_cfg["vars"]["interface"] = str(value)
            if scope.startswith("noc::subinterface"):
                alarm_cfg["vars"]["subinterface"] = str(value)
        if metric_config.threshold_profile.umbrella_filter_handler:
            if metric_config.threshold_profile.umbrella_filter_handler.allow_threshold_handler:
                try:
                    handler = metric_config.threshold_profile.umbrella_filter_handler.get_handler()
                    if handler:
                        alarm_cfg = handler(self, alarm_cfg)
                        if not alarm_cfg:
                            return []
                except Exception as e:
                    self.logger.error("Exception when loading handler %s", e)
            else:
                self.logger.warning("Umbrella filter Handler is not allowed for Thresholds")
        return [
            ProblemItem(
                alarm_class=threshold.alarm_class.name,
                path=[path],
                labels=labels or [],
                vars=alarm_cfg["vars"],
            )
        ]

    def get_event_cfg(
        self,
        metric_config,
        threshold_profile,
        threshold,
        event_class,
        path,
        value,
        labels=None,
        sensor=None,
        sla_probe=None,
    ):
        """
        Get configuration for umbrella alarm
        :param metric_config:
        :param threshold_profile:
        :param threshold:
        :param event_class:
        :param path:
        :param value:
        :param labels:
        :param sensor:
        :param sla_probe:
        :return: List of dicts or empty list
        """
        full_path = path
        if path != metric_config.metric_type.name:
            path = path.replace("%s |" % metric_config.metric_type.name, "")
        result = False
        raw_vars = {
            "path": path.strip(),
            "labels": ";".join(labels or []),
            "full_path": full_path,
            "threshold": threshold,
            "metric": metric_config.metric_type.name,
            "value": str(value),
            "window_type": threshold_profile.window_type,
            "window": str(threshold_profile.window),
            "window_function": threshold_profile.window_function,
        }
        if sensor:
            raw_vars["sensor"] = str(sensor)
        if sla_probe:
            raw_vars["sla_probe"] = str(sla_probe)
        if threshold_profile.umbrella_filter_handler:
            if threshold_profile.umbrella_filter_handler.allow_threshold_handler:
                try:
                    handler = threshold_profile.umbrella_filter_handler.get_handler()
                    if handler:
                        raw_vars = handler(self, raw_vars)
                        if not raw_vars:
                            return []
                except Exception as e:
                    self.logger.error("Exception when loading handler %s", e)
            else:
                self.logger.warning("Umbrella filter Handler is not allowed for Thresholds")
        try:
            self.raise_event(event_class, raw_vars)
            result = True
        except Exception as e:
            self.logger.error("Exception when send message %s", e)
        if result:
            return [raw_vars]
        return []

    def raise_event(self, event_class, raw_vars=None):
        if not raw_vars:
            raw_vars = {}
        data = {"$event": {"class": event_class, "vars": raw_vars}}
        msg = {"ts": time.time(), "object": self.object.id, "data": data}
        self.logger.info("Pub Event: %s", msg)
        stream, partition = self.object.events_stream_and_partition
        self.service.publish(
            orjson.dumps(msg),
            stream=stream,
            partition=partition,
        )
