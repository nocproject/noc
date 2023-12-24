# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List, Dict, Tuple

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, MetricCollectorConfig


class Script(GetMetricsScript):
    name = "IRE-Polus.Horizon.get_metrics"
    UNITS_MAP = {
        "сек": "s",
        "дБм": "dBm",
        "дБ": "dB",
        "°C": "C",
        "В": "VDC",
        "А": "A",
        "мА": "m,A",
        "мВт": "m,W",
        "%": "%",
    }

    def collect_sensor_metrics(self, metrics: List[MetricCollectorConfig]):
        """
        Collect sensor metrics method. Configured by profile
        :param metrics:
        :return:
        """
        # devices: Dict[int, Device] = {}  # slot -> device info
        sensor_map: Dict[Tuple[str, str], int] = {}
        for sensor in metrics:
            hints = sensor.get_hints()
            if "slot" not in hints:
                continue
            slot = hints["slot"]
            name = sensor.labels[0][13:]
            # labels - "noc::sensor::Time", "noc::slot::1"
            sensor_map[(slot, name)] = sensor.sensor
        # v = self.http.get("/api/devices", json=True)
        for slot in {x for x, _ in sensor_map}:
            v = self.http.get(
                f"/api/devices/params?crateId=1&slotNumber={slot}"
                f"&fields=name,value,description,measureUnit,performanceProcessing,sectionId",
                json=True,
            )
            for p in v["params"]:
                if (slot, p["name"]) not in sensor_map:
                    continue
                try:
                    value = float(p["value"])
                except ValueError:
                    continue
                units = self.UNITS_MAP.get(p["measureUnit"], "1")
                self.logger.debug(
                    "[%s|%s] Processed Dynamic param: %s", slot, p["name"], p["value"]
                )
                sensor = sensor_map[(slot, p["name"])]
                self.set_metric(
                    id=sensor,
                    metric="Sensor | Value",
                    labels=[f"noc::sensor::{p['name']}", f"noc::slot::{slot}"],
                    value=float(value),
                    units=units,
                    sensor=sensor,
                )
