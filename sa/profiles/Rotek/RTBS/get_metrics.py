# ----------------------------------------------------------------------
# Rotek.RTBS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
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
