# ---------------------------------------------------------------------
# ElectronR.KO01M.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "ElectronR.KO01M.get_metrics"

    @metrics(["Environment | Sensor Status"], volatile=False, access="S")  # SNMP version
    def get_sensor_status(self, metrics):
        for metric in metrics:
            value = 1
            if metric.ifindex == 100:
                continue
            elif metric.ifindex == 140:
                temp = self.snmp.get("1.3.6.1.4.1.35419.20.1.140.0", cached=True)
                if -55 < temp < 600:
                    value = 0
            elif metric.ifindex == 160:
                impulse = self.snmp.get("1.3.6.1.4.1.35419.20.1.160.0", cached=True)
                if impulse != 0:
                    value = 0
            else:
                res = self.snmp.get("1.3.6.1.4.1.35419.20.1.10%s.0" % metric.ifindex)
                if res == 1:
                    value = 0
            self.set_metric(
                id=("Environment | Sensor Status", metric.labels),
                value=value,
            )

    @metrics(["Environment | Temperature"], volatile=False, access="S")  # SNMP version
    def get_temperature(self, metrics):
        for metric in metrics:
            if metric.ifindex == 140:
                value = self.snmp.get("1.3.6.1.4.1.35419.20.1.%s.0" % metric.ifindex, cached=True)
                port = metric.labels[0].rsplit("::", 1)[-1]
                self.set_metric(
                    id=("Environment | Temperature", metric.labels),
                    labels=[f"noc::module::{port}", f"noc::name::{port}"],
                    value=value,
                    multi=True,
                )

    @metrics(["Environment | Voltage"], volatile=False, access="S")  # SNMP version
    def get_voltage(self, metrics):
        for metric in metrics:
            value = self.snmp.get("1.3.6.1.4.1.35419.20.1.%s.0" % metric.ifindex)
            port = metric.labels[0].rsplit("::", 1)[-1]
            self.set_metric(
                id=("Environment | Voltage", metric.labels),
                labels=[f"noc::module::{port}", f"noc::name::{port}"],
                value=value,
                multi=True,
            )

    @metrics(["Environment | Pulse"], volatile=False, access="S")  # SNMP version
    def get_pulse(self, metrics):
        for metric in metrics:
            if metric.ifindex == 160:
                value = self.snmp.get("1.3.6.1.4.1.35419.20.1.%s.0" % metric.ifindex, cached=True)
                port = metric.labels[0].rsplit("::", 1)[-1]
                self.set_metric(
                    id=("Environment | Pulse", metric.labels),
                    labels=[f"noc::name::{port}"],
                    value=value,
                )

    @metrics(["Environment | Power | Input | Status"], volatile=False, access="S")  # SNMP version
    def get_power_input_status(self, metrics):
        for metric in metrics:
            value = self.snmp.get("1.3.6.1.4.1.35419.20.1.10%s.0" % metric.ifindex, cached=True)
            self.set_metric(
                id=("Environment | Power | Input | Status", metric.labels),
                value=0 if value == 1 else 1,
            )
