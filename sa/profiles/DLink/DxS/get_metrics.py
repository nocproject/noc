# ----------------------------------------------------------------------
# DLink.DxS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.core.mib import mib


class Script(GetMetricsScript):
    name = "DLink.DxS.get_metrics"

    @metrics(["CPU | Usage"], volatile=False, access="S")
    def get_cpu_metrics(self, metrics):
        # DLINK-AGENT-MIB::agentCPUutilizationIn5sec
        cpu = self.snmp.get("1.3.6.1.4.1.171.12.1.1.6.1.0")
        if cpu is None:
            v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
            if v.startswith("DES-3200"):  # need testing
                cpu = self.snmp.get("1.3.6.1.4.1.171.12.1.1.6.1")
            elif v.startswith("DGS-3212SR") or v.startswith("DGS-3312SR"):
                cpu = self.snmp.get("1.3.6.1.4.1.171.11.55.2.2.1.4.1.0")

        if cpu is not None:
            self.set_metric(id=("CPU | Usage", None), value=round(float(cpu)))
