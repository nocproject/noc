# ----------------------------------------------------------------------
# Eltex.TAU.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "Eltex.TAU.get_metrics"

    @metrics(
        ["CPU | Usage"],
        volatile=False,
        access="S",
    )
    def get_cpu_usage(self, metrics):
        cpu_usage = float(self.snmp.get("1.3.6.1.4.1.35265.1.9.8.0", cached=True))
        if cpu_usage:
            self.set_metric(
                id=("CPU | Usage", None),
                value=int(cpu_usage),
                multi=True,
            )

    @metrics(
        ["Memory | Usage"],
        volatile=False,
        access="S",
    )
    def get_memory_free(self, metrics):
        v = self.snmp.get("1.3.6.1.4.1.35265.1.9.5.0", cached=True)
        if v:
            mem_usage = float(v[:-2]) / 446.44
            self.set_metric(
                id=("Memory | Usage", None),
                value=int(mem_usage),
                multi=True,
            )

    @metrics(
        ["Environment | Temperature"],
        volatile=False,
        access="S",
    )
    def get_temperature(self, metrics):
        v = self.snmp.get("1.3.6.1.4.1.35265.1.9.10.5.0", cached=True)
        if v:
            self.set_metric(
                id=("Environment | Temperature", None),
                path=["", "", "", "Temperature 1"],
                value=v,
                multi=True,
            )
        v = self.snmp.get("1.3.6.1.4.1.35265.1.9.10.6.0", cached=True)
        if v:
            self.set_metric(
                id=("Environment | Temperature", None),
                path=["", "", "", "Temperature 2"],
                value=v,
                multi=True,
            )
        v = self.snmp.get("1.3.6.1.4.1.35265.1.9.10.7.0", cached=True)
        if v:
            self.set_metric(
                id=("Environment | Temperature", None),
                path=["", "", "", "Temperature 3"],
                value=v,
                multi=True,
            )
        v = self.snmp.get("1.3.6.1.4.1.35265.1.9.10.8.0", cached=True)
        if v:
            self.set_metric(
                id=("Environment | Temperature", None),
                path=["", "", "", "Temperature 4"],
                value=v,
                multi=True,
            )

    @metrics(
        ["Environment | Sensor Status"],
        volatile=False,
        access="S",
    )
    def get_sensor_status(self, metrics):
        v = self.snmp.get("1.3.6.1.4.1.35265.1.9.10.9.0", cached=True)
        if v:
            self.set_metric(
                id=("Environment | Sensor Status", None),
                path=["", "", "", "Fan State"],
                value=v,
                multi=True,
            )
        v = self.snmp.get("1.3.6.1.4.1.35265.1.9.10.10.0", cached=True)
        if v:
            self.set_metric(
                id=("Environment | Sensor Status", None),
                path=["", "", "", "Fan 1 Rotate"],
                value=v,
                multi=True,
            )
        v = self.snmp.get("1.3.6.1.4.1.35265.1.9.10.11.0", cached=True)
        if v:
            self.set_metric(
                id=("Environment | Sensor Status", None),
                path=["", "", "", "Fan 2 Rotate"],
                value=v,
                multi=True,
            )
        v = self.snmp.get("1.3.6.1.4.1.35265.1.9.10.14.0", cached=True)
        if v:
            self.set_metric(
                id=("Environment | Sensor Status", None),
                path=["", "", "", "Device Power (ac/dc)"],
                value=v,
                multi=True,
            )
