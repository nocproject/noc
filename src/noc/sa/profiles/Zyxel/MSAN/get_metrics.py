# ---------------------------------------------------------------------
# Zyxel.MSAN.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from .oidrules.slot import SlotRule


class Script(GetMetricsScript):
    name = "Zyxel.MSAN.get_metrics"
    OID_RULES = [SlotRule]

    @metrics(["Object | MAC | TotalUsed"], access="S")  # SNMP version
    def get_count_mac_snmp(self, metrics):
        mac_num = self.snmp.get("1.3.6.1.2.1.17.7.1.2.1.1.2.0")
        if mac_num is not None:
            self.set_metric(id=("Object | MAC | TotalUsed", None), value=int(mac_num))

    @metrics(
        [
            "Environment | Temperature",
        ],
        access="S",  # SNMP version
    )
    def get_temp_sensor_metrics(self, metrics):
        if "Stack | Member Ids" in self.capabilities:
            hwSlotIndex = self.capabilities["Stack | Member Ids"].split(" | ")
            for si in hwSlotIndex:
                for oid, v in self.snmp.getnext(f"1.3.6.1.4.1.890.1.5.13.5.11.3.3.1.2.0.{si}"):
                    ssi = oid.split(".")[-1]
                    sensor_desc = self.snmp.get(f"1.3.6.1.4.1.890.1.5.13.5.11.3.3.1.6.0.{si}.{ssi}")
                    labels = [
                        f"noc::slot::{si}",
                        f"noc::sensor::temperature_{sensor_desc}",
                    ]
                    if v:
                        self.set_metric(
                            id=("Environment | Temperature", None),
                            metric="Environment | Temperature",
                            labels=labels,
                            value=int(v),
                            multi=True,
                            sensor=ssi,
                            units="C",
                        )
