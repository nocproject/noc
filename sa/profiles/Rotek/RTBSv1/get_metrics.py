# ----------------------------------------------------------------------
# Rotek.RTBSv1.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.core.validators import is_ipv4


class Script(GetMetricsScript):
    name = "Rotek.RTBSv1.get_metrics"

    @metrics(["Check | Result", "Check | RTT"], volatile=False, access="C")  # CLI version
    def get_avail_metrics(self, metrics):
        if not self.credentials["path"]:
            return
        for ip in self.credentials["path"].split(","):
            if is_ipv4(ip.strip()):
                result = self.scripts.ping(address=ip, count=4)
                self.set_metric(
                    id=("Check | Result", None),
                    metric="Check | Result",
                    labels=(
                        "noc::diagnostic::REMOTE_PING",
                        "noc::check::name::ping",
                        f"noc::check::arg0::{ip}",
                        "noc::check_name::ping",
                        f"noc::check_id::{ip}",
                    ),
                    value=bool(result["success"]),
                    multi=True,
                )
                if result["success"]:
                    self.set_metric(
                        id=("Check | RTT", None),
                        metric="Check | RTT",
                        labels=(
                            "noc::diagnostic::REMOTE_PING",
                            "noc::check::name::ping",
                            f"noc::check::arg0::{ip}",
                            "noc::check_name::ping",
                            f"noc::check_id::{ip}",
                        ),
                        value=bool(result["success"]),
                    )

    @metrics(["Memory | Total", "Memory | Usage"], volatile=False, access="S")  # SNMP version
    def get_memory_metrics(self, metrics):

        memory_total, memory_usage, *_ = (
            data for _, data in self.snmp.getnext("1.3.6.1.4.1.10002.1.1.1.1")
        )
        if memory_total and memory_usage:
            for metric in metrics:
                self.set_metric(
                    id=(
                        "Memory | Total" if "Memory | Total" in str(metric) else "Memory | Usage",
                        None,
                    ),
                    metric=(
                        "Memory | Total" if "Memory | Total" in str(metric) else "Memory | Usage"
                    ),
                    value=(
                        int(memory_total)
                        if "Memory | Total" in str(metric)
                        else int((memory_usage * 100) / memory_total)
                    ),
                    units="byte" if "Memory | Total" in str(metric) else "%",
                )

    @metrics(
        [
            "CPU | Load | 1min",
            "CPU | Load | 5min",
        ],
        volatile=False,
        access="S",
    )  # SNMP version
    def get_cpu_metrics(self, metrics):

        index_map = {1: "1", 2: "5"}
        for index in index_map.keys():
            value = self.snmp.get(f"1.3.6.1.4.1.10002.1.1.1.4.2.1.3.{index}")
            self.set_metric(
                id=(f"CPU | Load | {index_map.get(index)}min", None),
                metric=f"CPU | Load | {index_map.get(index)}min",
                value=float(value) if value else 0,
                units="%",
            )

    @metrics(["Object | MAC | TotalUsed"], volatile=False, access="S")  # SNMP version
    def get_mac_count(self, metrics):
        mac_count = len([mac for _, mac in self.snmp.getnext("1.3.6.1.4.1.41752.3.10.1.3.2.1.1")])
        if mac_count:
            self.set_metric(
                id=("Object | MAC | TotalUsed", None),
                metric="Object | MAC | TotalUsed",
                value=mac_count,
            )

    @metrics(
        ["Radio | Frequency", "Radio | Bandwidth", "Radio | Quality"],
        volatile=False,
        access="S",
    )  # SNMP version
    def get_radio_metrics(self, metrics):

        oid_index_map, base_oid = {
            "Radio | Frequency": 6,
            "Radio | Bandwidth": 8,
            "Radio | Quality": 12,
        }, "1.3.6.1.4.1.41752.3.10.1.2.1.1"

        iface = self.snmp.get(f"{base_oid}.4.6")
        for key, value in oid_index_map.items():
            response = self.snmp.get(f"{base_oid}.{str(value)}.6")
            if response:
                self.set_metric(
                    id=(key, None),
                    labels=[f"noc::interface::{iface}"],
                    metric=key,
                    value=response,
                    units="1" if key == "Radio | Quality" else "M,hz",
                )
