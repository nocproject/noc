# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, MetricCollectorConfig
from noc.core.script.metrics import scale, invert0
from .profile import PolusParam


class Script(GetMetricsScript):
    name = "IRE-Polus.Horizon.get_metrics"

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
