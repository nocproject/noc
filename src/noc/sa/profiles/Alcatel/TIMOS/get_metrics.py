# ----------------------------------------------------------------------
# Alcatel.TIMOS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "Alcatel.TIMOS.get_metrics"

    @metrics(
        ["Subscribers | Summary"],
        has_capability="BRAS | PPPoE",
        volatile=False,
        access="S",
    )
    def get_subscribers_metrics_snmp(self, metrics):
        """
        total sessions ['0', '', '', '']
        slot sessions ['0', <slot_num>, '', '']
        module sessions ['0', '', <module_num>, '']
        port sessions ['0', '', '', <port_name>]
        """
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.33.1.106.1.2.1", bulk=False):
            oid2 = oid.split("1.3.6.1.4.1.6527.3.1.2.33.1.106.1.2.1.")
            slot = "slot "
            slot += str(oid2[1])
            self.set_metric(
                id=("Subscribers | Summary", None),
                labels=("noc::chassis::0", f"noc::slot::{slot}"),
                value=int(v),
                multi=True,
            )
        names = {x: y for y, x in self.scripts.get_ifindexes().items()}
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.33.1.104.1.60.1", bulk=False):
            oid2 = oid.split("1.3.6.1.4.1.6527.3.1.2.33.1.104.1.60.1.")
            port = names[int(oid2[1])]
            self.set_metric(
                id=("Subscribers | Summary", None),
                labels=("noc::chassis::0", f"noc::interface::{port!s}"),
                value=int(v),
                multi=True,
            )
        metric = self.snmp.get("1.3.6.1.4.1.6527.3.1.2.33.5.9.1.2.1")
        self.set_metric(
            id=("Subscribers | Summary", None),
            labels=("noc::chassis::0",),
            value=int(metric),
            multi=True,
        )
