# ---------------------------------------------------------------------
# Qtech.QSW2800.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from .oidrules.slot import SlotRule
from .oidrules.enterprise import EnterpriseRule


class Script(GetMetricsScript):
    name = "Qtech.QSW2800.get_metrics"

    OID_RULES = [SlotRule, EnterpriseRule]
    BASE_DOM_OID = "1.3.6.1.4.1.27514.100.30.1.1"
    DOM_METRIC_INDEX = [
        ("Temperature", 2),
        ("Voltage", 7),
        ("Bias_Current", 12),
        ("RxPower", 17),
        ("TxPower", 22),
    ]

    def get_clean_dom_metric(self, metric_value):
        dom_metrics_marks = ["(A+)", "(A-)", "(W+)", "(W-)"]
        for mark in dom_metrics_marks:
            if mark in metric_value:
                metric_value = metric_value.replace(mark, "")
        return metric_value

    @metrics(
        [
            "Interface | DOM | Temperature",
            "Interface | DOM | Bias Current",
            "Interface | DOM | TxPower",
            "Interface | DOM | RxPower",
            "Interface | DOM | Voltage",
        ],
        access="S",
        volatile=False,
    )  # SNMP version
    def get_optical_transciever_metrics(self, metrics):
        for iface in metrics:
            ifindex = iface.ifindex
            ilabels = iface.labels

            dom_oid_dict = {
                m_name: f"{self.BASE_DOM_OID}.{i}.{ifindex}" for m_name, i in self.DOM_METRIC_INDEX
            }
            interface_dom_metrics = self.snmp.get(dom_oid_dict)

            if (
                interface_dom_metrics["Temperature"]
                and interface_dom_metrics["Temperature"] != "NULL"
            ):
                self.set_metric(
                    id=("Interface | DOM | Temperature", ilabels),
                    labels=ilabels,
                    value=float(self.get_clean_dom_metric(interface_dom_metrics["Temperature"])),
                    multi=True,
                    units="C",
                )

            if interface_dom_metrics["Voltage"] and interface_dom_metrics["Voltage"] != "NULL":
                self.set_metric(
                    id=("Interface | DOM | Voltage", ilabels),
                    labels=ilabels,
                    value=float(self.get_clean_dom_metric(interface_dom_metrics["Voltage"])),
                    multi=True,
                    units="VDC",
                )

            if (
                interface_dom_metrics["Bias_Current"]
                and interface_dom_metrics["Bias_Current"] != "NULL"
            ):
                self.set_metric(
                    id=("Interface | DOM | Bias Current", ilabels),
                    labels=ilabels,
                    value=float(self.get_clean_dom_metric(interface_dom_metrics["Bias_Current"])),
                    multi=True,
                    units="m,A",
                )

            if interface_dom_metrics["RxPower"] and interface_dom_metrics["RxPower"] != "NULL":
                self.set_metric(
                    id=("Interface | DOM | RxPower", ilabels),
                    labels=ilabels,
                    value=float(self.get_clean_dom_metric(interface_dom_metrics["RxPower"])),
                    multi=True,
                    units="dBm",
                )

            if interface_dom_metrics["TxPower"] and interface_dom_metrics["TxPower"] != "NULL":
                self.set_metric(
                    id=("Interface | DOM | TxPower", ilabels),
                    labels=ilabels,
                    value=float(self.get_clean_dom_metric(interface_dom_metrics["TxPower"])),
                    multi=True,
                    units="dBm",
                )

    @metrics(["Object | MAC | TotalUsed"], access="S")  # SNMP version
    def get_count_mac_snmp(self, metrics):
        mac_total_used = 0
        for _, mac_num in self.snmp.getnext("1.3.6.1.2.1.17.7.1.2.1.1.2"):
            if mac_num:
                mac_total_used += mac_num
        if mac_total_used:
            self.set_metric(id=("Object | MAC | TotalUsed", None), value=int(mac_total_used))
