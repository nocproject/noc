# ----------------------------------------------------------------------
# HP.OfficeConnect.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "HP.OfficeConnect.get_metrics"

    rx_cpu_usage = re.compile(
        r"\s*5 Secs\s+\(\s*(?P<usage_5sec>\d+\.\d+)%\)"
        r"\s+60 Secs\s+\(\s*(?P<usage_60sec>\d+\.\d+)%\)"
        r"\s*300 Secs\s*\(\s*(?P<usage_300sec>\d+\.\d+)%\)\s*",
    )

    @metrics(["CPU | Usage"], volatile=False, access="S")  # CLI version
    def get_cpu_metrics(self, metrics):
        # "    5 Secs (  8.5038%)   60 Secs ( 13.5686%)  300 Secs ( 12.9707%)"
        v = self.snmp.get("1.3.6.1.4.1.11.5.7.5.7.1.1.1.1.4.9.0")
        if not v:
            return
        match = self.rx_cpu_usage.match(v)
        if match:
            self.set_metric(
                id=("CPU | Usage", None),
                value=round(float(match.group("usage_60sec")) + 0.5),
                units="%",
            )
