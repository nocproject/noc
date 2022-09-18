# ---------------------------------------------------------------------
# Metric collector
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import itertools
import time
from typing import Any, List, Dict, Iterable

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.models.cfgmetrics import MetricCollectorConfig
from noc.inv.models.object import Object
from noc.inv.models.interfaceprofile import MetricConfig
from noc.inv.models.sensor import Sensor
from noc.sla.models.slaprobe import SLAProbe
from noc.config import config


MAX31 = 0x7FFFFFFF
MAX32 = 0xFFFFFFFF
MAX64 = 0xFFFFFFFFFFFFFFFF

NS = 1000000000.0

MT_COUNTER = "counter"
MT_BOOL = "bool"
MT_DELTA = "delta"
MT_COUNTER_DELTA = {MT_COUNTER, MT_DELTA}


class MetricsCheck(DiscoveryCheck):
    """
    MAC discovery
    """

    name = "metrics"
    required_script = "get_metrics"

    SLA_CAPS = ["Cisco | IP | SLA | Probes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_count = itertools.count()
        self.id_metrics: Dict[str, MetricConfig] = {}

    def iter_metric_sources(self) -> Iterable[MetricCollectorConfig]:
        """
        Iterate sources metric configs
        :return:
        """
        o: List[str] = Object.get_managed(self.object).values_list("id")
        for mc in self.object.iter_collected_metrics(
            is_box=self.is_box, is_periodic=self.is_periodic
        ):
            yield mc
        for sensor in Sensor.objects.filter(object__in=list(o)):
            for mc in sensor.iter_collected_metrics(
                is_box=self.is_box, is_periodic=self.is_periodic
            ):
                yield mc
        if not self.has_any_capability(self.SLA_CAPS):
            self.logger.info("SLA not configured, skipping SLA metrics")
            return
        for sla in SLAProbe.objects.filter(managed_object=self.object.id):
            for mc in sla.iter_collected_metrics(is_box=self.is_box, is_periodic=self.is_periodic):
                yield mc

    def handler(self):
        self.logger.info("Collecting metrics")
        # Build get_metrics input parameters
        metrics: List[Dict[str, Any]] = []
        s_data = {"managed_object": self.object.bi_id}
        for mc in self.iter_metric_sources():
            mc_metrics = []
            for m in mc.metrics:
                mt_name = m.name.replace(" ", "_")
                mc_metrics.append(m.name)
                if f"{m.name}.scope" in s_data:
                    continue
                s_data[f"{mt_name}.scope"] = m.scope_name
                s_data[f"{mt_name}.field"] = m.field_name
            metrics.append(
                {
                    "collector": mc.collector,
                    "metrics": mc_metrics,
                    "labels": mc.labels,
                    "hints": mc.hints,
                    "service": mc.service,
                    "sensor": mc.sensor,
                    "sla_probe": mc.sla_probe,
                }
            )
        if not metrics:
            self.logger.info("No metrics configured. Skipping")
            return
        #
        ts = time.time()
        if "last_run" in self.job.context and self.job.context["last_run"] < ts:
            self.job.context["time_delta"] = int(round(ts - self.job.context["last_run"]))
        self.job.context["last_run"] = ts
        self.logger.debug("Collecting metrics: %s", metrics)
        # Collect metrics
        result = [
            r
            for r in self.object.scripts.get_metrics(
                collected=metrics,
                streaming={
                    "stream": "metrics",
                    "partition": self.object.id % self.service.get_slot_limits("metrics"),
                    "utc_offset": config.tz_utc_offset,
                    "data": s_data,
                },
            )
        ]
        if not result:
            self.logger.info("No metrics found")
            return
        self.logger.info("Collected metrics: %s", len(result))
        # # Send metrics
        # if n_metrics:
        #   self.logger.info("Spooling %d metrics", n_metrics)
        #   for table in data:
        #      self.service.register_metrics(table, list(data[table].values()), key=self.object.id)

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
