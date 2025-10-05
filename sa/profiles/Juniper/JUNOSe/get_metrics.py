# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from .oidrules.slot import SlotRule
from noc.core.text import parse_table


class Script(GetMetricsScript):
    name = "Juniper.JUNOSe.get_metrics"
    OID_RULES = [SlotRule]

    @metrics(
        ["Subscribers | Summary"],
        has_capability="BRAS | PPTP",
        volatile=False,
        access="C",  # CLI version
    )
    def get_subscribers_metrics_slot_cli(self, metrics):
        """
        Returns collected subscribers metric in form
        slot id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        v = self.cli("show subscribers summary slot")
        v = v.splitlines()[:-2]
        v = "\n".join(v)
        r_v = parse_table(v)
        if len(r_v) >= 3:
            for slot, rtt in r_v.items():
                self.set_metric(
                    id=("Subscribers | Summary", None),
                    labels=("noc::chassis::0", f"noc::slot::{slot!s}"),
                    value=int(rtt),
                    multi=True,
                )

    @metrics(
        ["Subscribers | Summary"],
        has_capability="BRAS | PPPoE",
        volatile=False,
        access="S",
    )
    def get_subscribers_metrics_port_snmp(self, metrics):
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.4874.2.2.20.1.8.8.1.2", bulk=False):
            oid2 = oid.split("1.3.6.1.4.1.4874.2.2.20.1.8.8.1.2.")
            port = oid2[1][2:].replace(".", "/")
            self.set_metric(
                id=("Subscribers | Summary", None),
                labels=("noc::chassis::0", f"noc::interface::{port!s}"),
                value=int(v),
                multi=True,
            )
        metric = self.snmp.get("1.3.6.1.4.1.4874.2.2.20.1.8.3.0")
        self.set_metric(
            id=("Subscribers | Summary", None),
            labels=("noc::chassis::0",),
            value=int(metric),
            multi=True,
        )

    @metrics(
        ["Subscribers | Summary"],
        has_capability="BRAS | PPPoE",
        volatile=False,
        access="C",
    )
    def get_subscribers_metrics_port_cli(self, metrics):
        v = self.cli("show subscribers summary port")
        v = v.splitlines()[:-2]
        v = "\n".join(v)
        r_v = parse_table(v)
        if len(r_v) >= 1:
            for port, rtt in r_v.items():
                self.set_metric(
                    id=("Subscribers | Summary", None),
                    labels=("noc::chassis::0", f"noc::interface::{port!s}"),
                    value=int(rtt),
                    multi=True,
                )
