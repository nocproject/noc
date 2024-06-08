# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Telecom.FXS.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2023-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "Telecom.FXS.get_metrics"
    always_prefer = "S"

    @metrics(["Environment | Temperature"], volatile=False, access="S")  # SNMP version
    def get_sensor_temperature_metrics(self, metrics):
        oids = [
            "1.3.6.1.4.1.40248.4.1.104",
            "1.3.6.1.4.1.40248.4.1.105",
            "1.3.6.1.4.1.40248.4.1.106",
        ]
        for i, oid in enumerate(oids, 1):
            value = self.snmp.get(oid)
            if value == "empty":
                continue
            self.logger.info(f"v=={int(value.split('.',1)[0])}")
            if value is not None:
                self.set_metric(
                    id=("Environment | Temperature", None),
                    labels=(f"noc::sensor::Temperature Sensor{i}",),
                    value=int(value.split(".", 1)[0]),
                    multi=True,
                    units="C",
                )
