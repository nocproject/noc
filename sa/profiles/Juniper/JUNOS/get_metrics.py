# ---------------------------------------------------------------------
# Juniper.JUNOS.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from .oidrules.slot import SlotRule
from noc.core.mib import mib


class Script(GetMetricsScript):
    name = "Juniper.JUNOS.get_metrics"
    OID_RULES = [SlotRule]

    @metrics(
        ["Subscribers | Summary"],
        has_capability="Metrics | Subscribers",
        volatile=False,
        access="S",  # not CLI version
    )
    def get_subscribers_metrics(self, metrics):
        if self.is_gte_16:
            for oid, v in self.snmp.getnext("1.3.6.1.4.1.2636.3.64.1.1.1.5.1.3", bulk=False):
                oid2 = oid.split("1.3.6.1.4.1.2636.3.64.1.1.1.5.1.3.")
                interf = oid2[1].split(".")
                del interf[0]
                port = ""
                for x in interf:
                    port += chr(int(x))
                self.set_metric(
                    id=("Subscribers | Summary", None),
                    labels=("noc::chassis::0", f"noc::interface::{str(port)}"),
                    value=int(v),
                    multi=True,
                )
        metric = self.snmp.get("1.3.6.1.4.1.2636.3.64.1.1.1.2.0")
        self.set_metric(
            id=("Subscribers | Summary", None),
            labels=("noc::chassis::0",),
            value=int(metric),
            multi=True,
        )

    @metrics(
        [
            "Interface | CBQOS | Drops | Out | Delta",
            "Interface | CBQOS | Octets | Out",
            "Interface | CBQOS | Octets | Out | Delta",
            "Interface | CBQOS | Packets | Out",
            "Interface | CBQOS | Packets | Out | Delta",
        ],
        volatile=False,
        has_capability="Juniper | OID | jnxCosIfqStatsTable",
        access="S",  # CLI version
    )
    def get_interface_cbqos_metrics_snmp(self, metrics):
        ifaces = {str(m.ifindex): m.labels for m in metrics if m.ifindex}
        for ifindex in ifaces:
            for index, packets, octets, discards in self.snmp.get_tables(
                [
                    mib["JUNIPER-COS-MIB::jnxCosIfqTxedPkts", ifindex],
                    mib["JUNIPER-COS-MIB::jnxCosIfqTxedBytes", ifindex],
                    mib["JUNIPER-COS-MIB::jnxCosIfqTailDropPkts", ifindex],
                ]
            ):
                # ifindex, traffic_class = index.split(".", 1)
                # if ifindex not in ifaces:
                #    continue
                traffic_class = "".join([chr(int(x)) for x in index.split(".")[1:]])
                ts = self.get_ts()
                for metric, value in [
                    ("Interface | CBQOS | Drops | Out | Delta", discards),
                    ("Interface | CBQOS | Octets | Out | Delta", octets),
                    ("Interface | CBQOS | Octets | Out", octets),
                    ("Interface | CBQOS | Packets | Out | Delta", packets),
                    ("Interface | CBQOS | Packets | Out", packets),
                ]:
                    scale = 1
                    self.set_metric(
                        id=(metric, ifaces[ifindex]),
                        metric=metric,
                        value=float(value),
                        ts=ts,
                        labels=ifaces[ifindex] + [f"noc::traffic_class::{traffic_class}"],
                        multi=True,
                        type="delta" if metric.endswith("Delta") else "gauge",
                        scale=scale,
                    )
