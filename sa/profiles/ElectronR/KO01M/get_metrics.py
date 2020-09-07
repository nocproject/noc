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
            value = 0
            if metric.ifindex == 100:
                continue
            elif metric.ifindex == 140:
                temp = self.snmp.get("1.3.6.1.4.1.35419.20.1.140.0", cached=True)
                if -55 < temp < 600:
                    value = 1
            elif metric.ifindex == 160:
                impulse = self.snmp.get("1.3.6.1.4.1.35419.20.1.160.0", cached=True)
                if impulse != 0:
                    value = 1
            else:
                value = self.snmp.get("1.3.6.1.4.1.35419.20.1.10%s.0" % metric.ifindex)
            self.set_metric(
                id=("Environment | Sensor Status", metric.path), value=value,
            )

    @metrics(["Environment | Temperature"], volatile=False, access="S")  # SNMP version
    def get_temperature(self, metrics):
        for metric in metrics:
            value = self.snmp.get("1.3.6.1.4.1.35419.20.1.%s.0" % metric.ifindex, cached=True)
            self.set_metric(
                id=("Environment | Temperature", metric.path), value=value,
            )

    @metrics(["Environment | Voltage"], volatile=False, access="S")  # SNMP version
    def get_voltage(self, metrics):
        for metric in metrics:
            value = self.snmp.get("1.3.6.1.4.1.35419.20.1.%s.0" % metric.ifindex)
            self.set_metric(
                id=("Environment | Voltage", metric.path), value=value,
            )
