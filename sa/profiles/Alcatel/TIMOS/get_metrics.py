# ----------------------------------------------------------------------
# Alcatel.TIMOS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "Alcatel.TIMOS.get_metrics"

    @metrics(
        ["Subscribers | Summary"],
        has_capability="BRAS | IPoE",
        volatile=False,
        access="S",
    )
    def get_subscribers_metrics_snmp(self, metrics):
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.33.1.106.1.2.1", bulk=False):
            oid2 = oid.split("1.3.6.1.4.1.6527.3.1.2.33.1.106.1.2.1.")
            slot = "slot "
            slot += str(oid2[1])
            self.set_metric(
                id=("Subscribers | Summary", None),
                path=("0", slot, "slot"),
                value=int(v),
                multi=True,
            )
        names = {x: y for y, x in self.scripts.get_ifindexes().items()}
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.33.1.104.1.60.1", bulk=False):
            oid2 = oid.split("1.3.6.1.4.1.6527.3.1.2.33.1.104.1.60.1.")
            iface_name = names[int(oid2[1])]
            self.set_metric(
                id=("Subscribers | Summary", None),
                path=("0", iface_name, "port"),
                value=int(v),
                multi=True,
            )
        metric = self.snmp.get("1.3.6.1.4.1.6527.3.1.2.33.5.9.1.2.1")
        self.set_metric(
            id=("Subscribers | Summary", None),
            path=("0", "Total Subscribers", ""),
            value=int(metric),
            multi=True,
        )
