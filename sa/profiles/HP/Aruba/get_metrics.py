# ---------------------------------------------------------------------
# HP.Aruba.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.core.mib import mib


class Script(GetMetricsScript):
    name = "HP.Aruba.get_metrics"

    @metrics(
        ["CPU | Usage"],
        has_capability="SNMP | HOST-RESOURCES-MIB | CPU Cores | Idx",
        access="S",
    )
    def get_host_resource_cpu_usage(self, metrics):
        idx = [
            int(x)
            for x in self.capabilities["SNMP | HOST-RESOURCES-MIB | CPU Cores | Idx"].split(" | ")
        ]
        oids = {}
        for x in idx:
            oids[f"name.{x}"] = mib["HOST-RESOURCES-MIB::hrProcessorFrwID", x]
            oids[x] = mib["HOST-RESOURCES-MIB::hrProcessorLoad", x]
        if not oids:
            return
        result = self.snmp.get(oids)
        ts = self.get_ts()
        for x in idx:
            if x not in result:
                continue
            slot = result[f"name.{x}"]
            self.set_metric(
                id=x,
                metric="CPU | Usage",
                value=float(result[x]),
                ts=ts,
                labels=[f"noc::cpu::{slot}.{x}"],
                units="%",
            )
