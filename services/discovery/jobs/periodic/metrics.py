# ---------------------------------------------------------------------
# Metric collector
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any, List, Dict

# NOC modules
from noc.core.jsonutils import iter_chunks
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.pm.models.metrictype import MetricType
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
    Metric discovery
    """

    name = "metrics"
    required_script = "get_metrics"

    SLA_CAPS = ["Cisco | IP | SLA | Probes"]

    def handler(self):
        self.logger.info("Collecting metrics")
        # Build get_metrics input parameters
        metrics: List[Dict[str, Any]] = []
        #
        s_data = {"managed_object": self.object.bi_id}
        interval = self.job.get_interval() or self.object.get_metric_discovery_interval()
        runs = self.job.get_runs()
        self.logger.debug("Running with interval: %s:%s", interval, runs)
        for mc in self.object.iter_collected_metrics(runs, d_interval=interval):
            mc_metrics = []
            for m in mc.metrics:
                mt_name = m.name.replace(" ", "_")
                mc_metrics.append(m.name)
                if f"{m.name}.scope" in s_data:
                    continue
                s_data[f"{mt_name}.scope"] = m.scope_name
                s_data[f"{mt_name}.field"] = m.field_name
            if not mc_metrics:
                continue
            metrics.append(
                {
                    "collector": mc.collector,
                    "metrics": mc_metrics,
                    "labels": mc.labels,
                    "hints": mc.hints,
                    "service": mc.service,
                    "sensor": mc.sensor,
                    "sla_probe": mc.sla_probe,
                    "cpe": mc.cpe,
                }
            )
        if not metrics:
            self.logger.info("No metrics configured. Skipping...")
            return
        metrics_svc_slots = self.service.get_slot_limits("metrics")
        if not metrics_svc_slots:
            self.logger.warning("No active Metrics service. Skipping...")
            return
        self.logger.debug("Collecting metrics: %s", metrics)
        result = self.object.scripts.get_metrics(
            collected=metrics,
            streaming=(
                {
                    "stream": "metrics",
                    "partition": self.object.bi_id % metrics_svc_slots,
                    "utc_offset": config.tz_utc_offset,
                    "data": s_data,
                }
                if not config.discovery.proxy_metric
                else None
            ),
        )
        # Collect metrics
        if config.discovery.proxy_metric and not result:
            self.logger.info("No metrics found")
            return
        elif not config.discovery.proxy_metric and "metrics" in result:
            self.logger.info("Collected metrics: %s", result["metrics"]["n_measurements"])
            return
        elif not config.discovery.proxy_metric:
            return
        self.logger.info("Collected metrics: %s", len(result))
        # Send metrics
        for d in iter_chunks(
            self.clean_result(result),
            max_size=config.msgstream.max_message_size,
        ):
            self.service.publish(
                value=d,
                stream="metrics",
                partition=self.object.bi_id % metrics_svc_slots,
                headers={},
            )
        # # Send metrics
        # if n_metrics:
        #   self.logger.info("Spooling %d metrics", n_metrics)
        #   for table in data:
        #      self.service.register_metrics(table, list(data[table].values()), key=self.object.id)

    def clean_result(self, result):
        """
        Clean result for send to Metrics Service
        :param result:
        :return:
        """
        data = {}
        for rr in result:
            mt = MetricType.get_by_name(rr["metric"])
            scope_name = mt.scope.table_name
            m_id = (scope_name, tuple(rr.get("labels", [])))
            if m_id not in data:
                data[m_id] = {
                    "ts": rr["ts"] + config.tz_utc_offset * NS,
                    "managed_object": self.object.bi_id,
                    "scope": scope_name,
                    "field": mt.field_name,
                    "labels": rr.get("labels", []),
                    "_units": {},
                }
                if rr.get("sensor"):
                    data[m_id]["sensor"] = rr["sensor"]
                if rr.get("sla_probe"):
                    data[m_id]["sla_probe"] = rr["sla_probe"]
                if rr.get("service"):
                    data[m_id]["service"] = rr["service"]
                # if rr.get("cpe"):
                # For CPE used ID as ManagedObject
                #    data[m_id]["managed_object"] = rr["cpe"]
            data[m_id][mt.field_name] = rr["value"]
            data[m_id]["_units"][mt.field_name] = rr["units"]
        return list(data.values())

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
