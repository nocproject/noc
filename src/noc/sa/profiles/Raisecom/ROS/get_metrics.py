# ----------------------------------------------------------------------
# Raisecom.ROS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.text import parse_kv
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "Raisecom.ROS.get_metrics"
    mac_count_kv_map = {"total         mac address count": "mac_count"}

    @metrics(["Object | MAC | TotalUsed"], access="S", matcher="is_not_iscom2608g")  # SNMP version
    def get_count_mac_snmp(self, metrics):
        mac_num = self.snmp.get("1.3.6.1.2.1.17.7.1.2.1.1.2")
        if mac_num is not None:
            self.set_metric(id=("Object | MAC | TotalUsed", None), value=int(mac_num))

    @metrics(["Object | MAC | TotalUsed"], access="C", matcher="is_iscom2624g")  # CLI version
    def get_count_mac_cli(self, metrics):
        try:
            c = self.cli("show mac-address count ")
            mac_count = parse_kv(self.mac_count_kv_map, c)
            if mac_count is not None:
                mac_num = mac_count["mac_count"].strip()
                self.set_metric(id=("Object | MAC | TotalUsed", None), value=int(mac_num))
        except self.CLISyntaxError:
            raise NotADirectoryError

    @metrics(
        [
            "Object | MAC | TotalUsed",
        ],
        access="S",  # SNMP version
        matcher="is_iscom2924g",
        volatile=False,
    )
    def get_count_mac(self, metrics):
        mac_count = 0
        for oid, v in self.snmp.getnext("1.3.6.1.2.1.17.7.1.2.1.1.2"):
            mac_count = mac_count + v
        self.set_metric(
            id=("Object | MAC | TotalUsed", None),
            value=int(mac_count),
            multi=True,
        )
