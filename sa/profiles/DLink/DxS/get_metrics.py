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
                    scale=1000000,
                    units="bit/s",
                )
