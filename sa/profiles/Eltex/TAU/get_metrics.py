# ----------------------------------------------------------------------
# Eltex.TAU.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "Eltex.TAU.get_metrics"

    @metrics(
        ["CPU | Usage"],
        has_capability="SNMP | OID | fxsMonitoring",
        volatile=False,
        access="S",
    )
    def get_cpu_usage(self, metrics):
        cpu_usage = float(self.snmp.get("1.3.6.1.4.1.35265.1.9.8.0", cached=True))
        self.set_metric(
            id=("CPU | Usage", None),
            path=["", "", "", ""],
            value=int(cpu_usage),
            multi=True,
        )

    @metrics(
        ["Memory | Usage"],
        has_capability="SNMP | OID | fxsMonitoring",
        volatile=False,
        access="S",
    )
    def get_memory_free(self, metrics):
        v = self.snmp.get("1.3.6.1.4.1.35265.1.9.4.0", cached=True)
        mem_usage = float(v[:-2]) / 446.44
        self.set_metric(
            id=("Memory | Usage", None),
            path=[""],
            value=int(mem_usage),
            multi=True,
        )
