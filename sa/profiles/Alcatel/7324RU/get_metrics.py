# ---------------------------------------------------------------------
# Alcatel.7324RU.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "Alcatel.7324RU.get_metrics"

    @metrics(["Object | MAC | TotalUsed"], volatile=False, access="S")  # SNMP version
    def get_mac_totalused(self, metrics):
        """
        get quantity of mac_addresses
        """
        mac_total_used = 0

        for mac in self.snmp.getnext("1.3.6.1.2.1.17.4.3.1.1"):
            if mac:
                mac_total_used += 1

        if mac_total_used:
            self.set_metric(id=("Object | MAC | TotalUsed", None), value=mac_total_used)
