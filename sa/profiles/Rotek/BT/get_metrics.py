# ---------------------------------------------------------------------
# Rotek.BT.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.core.validators import is_float
from noc.core.script.metrics import scale


class Script(GetMetricsScript):
    name = "Rotek.BT.get_metrics"

    SENSOR_OID_SCALE = {
        "1.3.6.1.4.1.41752.911.10.1.2.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.3.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.4.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.5.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.6.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.2.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.3.0": scale(0.001, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.4.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.5.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.6.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.7.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.8.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.9.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.10.0": scale(0.000001, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.13.0": scale(0.001, 2),
    }

    @metrics(["Environment | Sensor Status"], volatile=False, access="S")  # SNMP version
    def get_sensor_status(self, metrics):
        for metric in metrics:
            port = metric.labels[0].rsplit("::", 1)[-1]
            if "st" in port:
                continue
            value = 1
            port = metric.labels[0].rsplit("::", 1)[-1]
            status = self.snmp.get(f"1.3.6.1.4.1.41752.5.15.1.{metric.ifindex}.0")
            if status is None:
                continue
            if metric.ifindex == 1 and int(status) == 0:
                value = 0
            elif metric.ifindex == 2:
                if is_float(status) and (-55 < float(status) < 600):
                    value = 0
            elif metric.ifindex in [4, 6] and float(status) > 0:
                value = 0
            elif metric.ifindex == 9 and int(status) != 2:
                value = 0
            self.set_metric(
                id=("Environment | Sensor Status", metric.labels),
                labels=[f"noc::sensor::{port}"],
                value=value,
            )

    @metrics(["Environment | Temperature"], volatile=False, access="S")  # SNMP version
    def get_temperature(self, metrics):
        for metric in metrics:
            if not metric.labels:
                continue
            port = metric.labels[0].rsplit("::", 1)[-1]
            if "temp" in port:
                value = self.snmp.get(f"1.3.6.1.4.1.41752.5.15.1.{metric.ifindex}.0")
                if value is None:
                    continue
                if is_float(value):
                    self.set_metric(
                        id=("Environment | Temperature", metric.labels),
                        labels=[f"noc::module::{port}", f"noc::sensor::{port}"],
                        value=value,
                        multi=True,
                    )

    @metrics(["Environment | Voltage"], volatile=False, access="S")  # SNMP version
    def get_voltage(self, metrics):
        for metric in metrics:
            value = self.snmp.get(f"1.3.6.1.4.1.41752.5.15.1.{metric.ifindex}.0")
            if value is None:
                continue
            port = metric.labels[0].rsplit("::", 1)[-1]
            self.set_metric(
                id=("Environment | Voltage", metric.labels),
                labels=["noc::module::battery", f"noc::sensor::{port}"],
                value=value,
                multi=True,
            )

    @metrics(["Environment | Power | Input | Status"], volatile=False, access="S")  # SNMP version
    def get_power_input_status(self, metrics):
        for metric in metrics:
            value = 1
            res = self.snmp.get("1.3.6.1.4.1.41752.5.15.1.9.0")
            port = metric.labels[0].rsplit("::", 1)[-1]
            if res not in [1, 2, 3]:
                value = 0
            self.set_metric(
                id=("Environment | Power | Input | Status", metric.labels),
                labels=[f"noc::sensor::{port}"],
                value=value,
            )
