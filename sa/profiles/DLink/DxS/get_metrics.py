# ----------------------------------------------------------------------
# DLink.DxS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.core.mib import mib
from noc.core.script.metrics import scale


class Script(GetMetricsScript):
    name = "DLink.DxS.get_metrics"

    @metrics(
        ["CPU | Usage"],
        has_capability="Metrics | OID | CPU | Usage | Value",
        volatile=False,
        access="S",
    )
    def get_cpu_metrics(self, metrics):
        # DLINK-AGENT-MIB::agentCPUutilizationIn5sec
        oid = self.capabilities.get("Metrics | OID | CPU | Usage | Value")
        if oid:
            try:
                cpu = self.snmp.get(oid)
                self.logger.debug("[CPU OID %s] ", cpu)
                if cpu is not None:
                    self.set_metric(id=("CPU | Usage", None), value=round(float(cpu)), units="%")
            except Exception:
                pass

    @metrics(["Interface | Speed"], volatile=False, access="S")
    def get_interface_speed(self, metrics):
        oids = {mib["IF-MIB::ifSpeed", m.ifindex]: m for m in metrics if m.ifindex}
        result = self.snmp.get_chunked(
            oids=list(oids),
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout(),
        )
        ts = self.get_ts()
        high_speed_oids = {}
        for r in result:
            mc = oids[r]
            if result[r] in {1410065408, 4294967295}:
                # Need ifHighSpeed metric
                high_speed_oids[mib["IF-MIB::ifHighSpeed", mc.ifindex]] = mc
                continue
            elif result[r] is None:
                continue
            self.set_metric(
                id=mc.id,
                metric=mc.metric,
                value=float(result[r]),
                ts=ts,
                labels=mc.labels,
                type="gauge",
                scale=1,
                units="bit/s",
            )
        # Getting ifHighSpeed
        if high_speed_oids:
            self.logger.info("[Interface | Speed] Getting ifHighSpeed oids: %s", high_speed_oids)
            results = self.snmp.get_chunked(
                oids=list(high_speed_oids),
                chunk_size=self.get_snmp_metrics_get_chunk(),
                timeout_limits=self.get_snmp_metrics_get_timeout(),
            )
            for r in results:
                mc = high_speed_oids[r]
                self.set_metric(
                    id=mc.id,
                    metric=mc.metric,
                    value=float(results[r]),
                    ts=ts,
                    labels=mc.labels,
                    type="gauge",
                    scale=scale(1000000),
                    units="bit/s",
                )

    @metrics(
        [
            "Memory | Usage",
            "Memory | Total",
        ],
        access="S",
        volatile=False,
        matcher="is_des3200",
    )
    def get_memory_usage(self, metrics):
        mem_total = self.snmp.get("1.3.6.1.4.1.171.12.1.1.9.1.2")
        if not mem_total:
            mem_total = self.snmp.get("1.3.6.1.4.1.171.10.75.10.2.1.2.1")
        if mem_total:
            self.set_metric(id=("Memory | Total", None), value=mem_total, multi=True, units="byte")

        mem_usage_prc = self.snmp.get("1.3.6.1.4.1.171.10.75.15.2.100.2.1")
        if not mem_usage_prc and mem_total:
            mem_usage = self.snmp.get("1.3.6.1.4.1.171.12.1.1.9.1.3")
            mem_usage_prc = mem_usage / mem_total * 100

        if mem_usage_prc:
            self.set_metric(
                id=("Memory | Usage", None), value=int(mem_usage), multi=True, units="%"
            )
