# ----------------------------------------------------------------------
# Rotek.RTBS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from .oidrules.platform import PlatformRule
from noc.core.validators import is_ipv4


class Script(GetMetricsScript):
    name = "Rotek.RTBS.get_metrics"
    OID_RULES = [PlatformRule]

    @metrics(["Check | Result", "Check | RTT"], volatile=False, access="C")  # CLI version
    def get_avail_metrics(self, metrics):
        if not self.credentials["path"]:
            return
        for ip in self.credentials["path"].split(","):
            if is_ipv4(ip.strip()):
                result = self.scripts.ping(address=ip)
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
                        value=result["avg"],
                    )

    @metrics(["Object | MAC | TotalUsed"], volatile=False, access="S")  # SNMP version
    def get_mac_totalused_snmp(self, metrics):
        response = [mac for _, mac in self.snmp.getnext("1.3.6.1.4.1.41752.3.5.1.3.2.1.1.8.6")]
        if response:
            self.set_metric(
                id=("Object | MAC | TotalUsed", None),
                metric="Object | MAC | TotalUsed",
                value=len(response),
            )

    @metrics(
        [
            "Radio | Frequency",
            "Radio | Bandwidth",
        ],
        volatile=False,
        access="S",
    )  # SNMP version
    def get_radio_metrics(self, metrics):

        oid_index_map, base_oid = {
            "Radio | Frequency": 7,
            "Radio | Bandwidth": 9,
        }, "1.3.6.1.4.1.41752.3.5.1.2.1.1"

        iface = self.snmp.get(f"{base_oid}.4.8")
        for key, value in oid_index_map.items():
            response = self.snmp.get(f"{base_oid}.{str(value)}.8")
            if response:
                self.set_metric(
                    id=(key, None),
                    labels=[f"noc::interface::{iface}"],
                    metric=key,
                    value=response,
                    units="M,hz",
                )
