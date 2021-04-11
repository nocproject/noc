# ---------------------------------------------------------------------
# Huawei.VRP.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from .oidrules.slot import SlotRule
from .oidrules.sslot import SSlotRule
from noc.core.mib import mib


class Script(GetMetricsScript):
    name = "Huawei.VRP.get_metrics"

    OID_RULES = [SlotRule, SSlotRule]

    @metrics(
        ["Interface | Status | Duplex"],
        has_capability="DB | Interfaces",
        matcher="is_cx200X",
        volatile=False,
        access="S",
    )
    def get_duplex_interface_metrics(self, metrics):
        if_map = {
            m.ifindex: m.labels
            for m in metrics
            if m.ifindex and m.metric == "Interface | Status | Duplex"
        }
        for oid, duplex in self.snmp.getnext(mib["EtherLike-MIB::dot3StatsDuplexStatus"]):
            _, ifindex = oid.rsplit(".", 1)
            if int(ifindex) not in if_map:
                continue
            self.set_metric(id=("Interface | Status | Duplex", if_map[int(ifindex)]), value=duplex)

    @metrics(
        ["Subscribers | Summary"],
        has_capability="BRAS | PPPoE",
        volatile=False,
        access="S",  # not CLI version
    )
    def get_subscribers_metrics(self, metrics):
        if "Slot | Member Ids" in self.capabilities:
            hwSlotIndex = self.capabilities["Slot | Member Ids"].split(" | ")
            for si in hwSlotIndex:
                for mi in [0, 1]:
                    v = self.snmp.get(f"1.3.6.1.4.1.2011.5.2.1.33.1.8.{si}.{mi}")
                    if v:
                        self.set_metric(
                            id=("Subscribers | Summary", None),
                            labels=("noc::chassis::0", f"noc::slot::{si}", f"noc::module::{mi}"),
                            value=int(v),
                            multi=True,
                        )
        v = self.snmp.get("1.3.6.1.4.1.2011.5.2.1.14.1.2.0")
        if v:
            self.set_metric(
                id=("Subscribers | Summary", None),
                labels=[],
                value=int(v),
                multi=True,
            )

    # @metrics(
    #     ["Interface | Errors | CRC", "Interface | Errors | Frame"],
    #     has_capability="DB | Interfaces",
    #     volatile=False,
    #     access="C",  # CLI version
    # )
    # def get_vrp_interface_metrics(self, metrics):
    #     v = self.cli("display interface")
    #     ifdata = self.profile.parse_ifaces(v)
    #     for iface, data in ifdata.items():
    #         iface = self.profile.convert_interface_name(iface)
    #         ipath = ["", "", "", iface]
    #         if "CRC" in data:
    #             self.set_metric(id=("Interface | Errors | CRC", ipath), value=int(data["CRC"]))
    #         if "Frames" in data:
    #             self.set_metric(id=("Interface | Errors | Frame", ipath), value=int(data["Frames"]))
