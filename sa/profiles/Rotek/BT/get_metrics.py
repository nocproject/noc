# ---------------------------------------------------------------------
# Rotek.BT.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.core.validators import is_float


class Script(GetMetricsScript):
    name = "Rotek.BT.get_metrics"

    @metrics(["Environment | Sensor Status"], volatile=False, access="S")  # SNMP version
    def get_sensor_status(self, metrics):
        for metric in metrics:
            port = metric.labels[0].rsplit("::", 1)[-1]
            if "st" in port:
                continue
            value = 1
            status = self.snmp.get("1.3.6.1.4.1.41752.5.15.1.%s.0" % metric.ifindex)
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
                value=value,
            )

    @metrics(["Environment | Temperature"], volatile=False, access="S")  # SNMP version
    def get_temperature(self, metrics):
        for metric in metrics:
            port = metric.labels[0].rsplit("::", 1)[-1]
            if "temp" in port:
                value = self.snmp.get("1.3.6.1.4.1.41752.5.15.1.%s.0" % metric.ifindex)
                if is_float(value):
                    self.set_metric(
                        id=("Environment | Temperature", metric.labels),
                        labels=[f"noc::module::{port}", f"noc::name::{port}"],
                        value=value,
                        multi=True,
                    )

    @metrics(["Environment | Voltage"], volatile=False, access="S")  # SNMP version
    def get_voltage(self, metrics):
        for metric in metrics:
            value = self.snmp.get("1.3.6.1.4.1.41752.5.15.1.%s.0" % metric.ifindex)
            port = metric.labels[0].rsplit("::", 1)[-1]
            self.set_metric(
                id=("Environment | Voltage", metric.labels),
                labels=["noc::module::battery", f"noc::name::{port}"],
                value=value,
                multi=True,
            )

    @metrics(["Environment | Power | Input | Status"], volatile=False, access="S")  # SNMP version
    def get_power_input_status(self, metrics):
        for metric in metrics:
            value = 1
            res = self.snmp.get("1.3.6.1.4.1.41752.5.15.1.9.0")
            if res not in [1, 2, 3]:
                value = 0
            self.set_metric(id=("Environment | Power | Input | Status", metric.labels), value=value)
