# ---------------------------------------------------------------------
# EdgeCore.ES.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "EdgeCore.ES.get_metrics"

    metric_map = {
        "CRC Align Errors": "Interface | Errors | CRC",
        "Frames Too Long": "Interface | Errors | Frame",
    }

    # @metrics(
    #     ["Interface | Errors | CRC", "Interface | Errors | Frame"],
    #     has_capability="DB | Interfaces",
    #     volatile=False,
    #     access="C",
    # )
    # def get_errors_interface_metrics(self, metrics):
    #     v = self.cli("show interfaces counters")
    #     v = self.profile.parse_ifaces(v)
    #
    #     ts = self.get_ts()
    #     print(v)
    #     for metric in self.metric_map:
    #         for iface in v:
    #             if metric not in v[iface]:
    #                 continue
    #             self.set_metric(
    #                 id=(metric, f"noc::interface::{self.profile.convert_interface_name(iface)}"),
    #                 metric=metric,
    #                 labels=[f"noc::interface::{self.profile.convert_interface_name(iface)}"],
    #                 value=int(v[iface][metric]),
    #                 ts=ts,
    #                 multi=True,
    #                 units="pkt",
    #             )
    #
