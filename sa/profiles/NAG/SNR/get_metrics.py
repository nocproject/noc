# ----------------------------------------------------------------------
# NAG.SNR.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.core.mib import mib


class Script(GetMetricsScript):
    name = "NAG.SNR.get_metrics"

    BASE_DOM_OID = "1.3.6.1.4.1.40418.7.100.30.1.1"
    DOM_METRIC_INDEX = [
        ("Temperature", 2),
        ("Voltage", 7),
        ("Bias Current", 12),
        ("RxPower", 17),
        ("TxPower", 22),
    ]

    BASE_POE_OID = "1.3.6.1.4.1.40418.7.100.26.10.1"
    POE_METRICS_INDEX = [("Power", 5), ("Current", 6), ("Voltage", 7)]

    def clean_value(self, value):
        chars_for_clean = ["(W+)", "(A+)", "(W-)", "(A-)"]
        for char in chars_for_clean:
            if char in value:
                value = value.replace(char, "")
        return value

    @metrics(
        [
            "Interface | DOM | Temperature",
            "Interface | DOM | Voltage",
            "Interface | DOM | Bias Current",
            "Interface | DOM | RxPower",
            "Interface | DOM | TxPower",
        ],
        volatile=False,
        access="S",
    )  # SNMP version
    def get_transceiver_metrics(self, metrics):
        for metric in metrics:
            dom_oid = {
                name: f"{self.BASE_DOM_OID}.{metric_index}"
                for name, metric_index in self.DOM_METRIC_INDEX
            }

            if dom_oid["Temperature"]:
                for oid, value in self.snmp.getnext(dom_oid.get("Temperature")):
                    if value != "NULL":
                        self.set_metric(
                            id=("Interface | DOM | Temperature", None),
                            labels=[f"noc::interface::Ethernet1/0/{oid.split('.')[-1]}"],
                            value=float(self.clean_value(value)),
                            multi=True,
                            units="C",
                        )

            if dom_oid["Voltage"]:
                for oid, value in self.snmp.getnext(dom_oid.get("Voltage")):
                    if value != "NULL":
                        self.set_metric(
                            id=("Interface | DOM | Voltage", None),
                            labels=[f"noc::interface::Ethernet1/0/{oid.split('.')[-1]}"],
                            value=float(self.clean_value(value)),
                            multi=True,
                            units="VDC",
                        )

            if dom_oid["Bias Current"]:
                for oid, value in self.snmp.getnext(dom_oid.get("Bias Current")):
                    if value != "NULL":
                        self.set_metric(
                            id=("Interface | DOM | Bias Current", None),
                            labels=[f"noc::interface::Ethernet1/0/{oid.split('.')[-1]}"],
                            value=float(self.clean_value(value)),
                            multi=True,
                            units="m,A",
                        )

            if dom_oid["RxPower"]:
                for oid, value in self.snmp.getnext(dom_oid.get("RxPower")):
                    if value != "NULL":
                        self.set_metric(
                            id=("Interface | DOM | RxPower", None),
                            labels=[f"noc::interface::Ethernet1/0/{oid.split('.')[-1]}"],
                            value=float(self.clean_value(value)),
                            multi=True,
                            units="dBm",
                        )

            if dom_oid["TxPower"]:
                for oid, value in self.snmp.getnext(dom_oid.get("TxPower")):
                    if value != "NULL":
                        self.set_metric(
                            id=("Interface | DOM | TxPower", None),
                            labels=[f"noc::interface::Ethernet1/0/{oid.split('.')[-1]}"],
                            value=float(self.clean_value(value)),
                            multi=True,
                            units="dBm",
                        )

    @metrics(["Object | MAC | TotalUsed"], volatile=False, access="S")  # SNMP version
    def get_mac_totalused(self, metrics):
        macs = [mac for mac in self.snmp.getnext(mib["BRIDGE-MIB::dot1dTpFdbAddress"]) if mac]
        if macs:
            self.set_metric(id=("Object | MAC | TotalUsed", None), value=len(macs))

    @metrics(["Environment | Temperature"], volatile=False, access="S")  # SNMP version
    def get_temperature(self, metrics):
        value = self.snmp.get(mib["NAG-MIB::switchTemperature", 0])
        if value:
            self.set_metric(id=("Environment | Temperature", None), value=int(value), units="C")

    @metrics(["CPU | Usage"], volatile=False, access="S")
    def get_cpu_metrics(self, metrics):
        cpu = self.snmp.get(mib["NAG-MIB::switchCpuUsage", 0])
        if cpu is not None:
            self.set_metric(id=("CPU | Usage", None), value=round(float(cpu)), units="%")

    @metrics(["Memory | Total", "Memory | Usage"], volatile=False, access="S")  # SNMP version
    def get_memory_metrics(self, metrics):
        value_total = self.snmp.get(mib["NAG-MIB::switchMemorySize", 0])  # bytes
        value_usage = self.snmp.get(mib["NAG-MIB::switchMemoryBusy", 0])  # bytes
        for metric in metrics:
            if "Memory | Total" in str(metric):
                if value_total:
                    self.set_metric(
                        id=("Memory | Total", None), value=int(value_total), units="bytes"
                    )
            if "Memory | Usage" in str(metric):
                if value_total and value_usage:
                    self.set_metric(
                        id=("Memory | Usage", None),
                        value=int((value_usage * 100) / value_total),
                        units="%",
                    )

    @metrics(
        ["Interface | PoE | Power", "Interface | PoE | Current", "Interface | PoE | Voltage"],
        volatile=False,
        access="S",
    )  # SNMP version
    def get_poe_metrics(self, metrics):
        for metric in metrics:

            poe_oid = {
                name: f"{self.BASE_POE_OID}.{metric_index}"
                for name, metric_index in self.POE_METRICS_INDEX
            }

            if poe_oid["Power"]:
                for oid, power in self.snmp.getnext(poe_oid.get("Power")):
                    self.set_metric(
                        id=("Interface | PoE | Power", None),
                        labels=[f"noc::interface::Ethernet1/0/{oid.split('.')[-1]}"],
                        value=power,
                        multi=True,
                        units="mW",
                    )

            if poe_oid["Current"]:
                for oid, current in self.snmp.getnext(poe_oid.get("Current")):
                    self.set_metric(
                        id=("Interface | PoE | Current", None),
                        labels=[f"noc::interface::Ethernet1/0/{oid.split('.')[-1]}"],
                        value=current,
                        multi=True,
                        units="mA",
                    )

            if poe_oid["Voltage"]:
                for oid, voltage in self.snmp.getnext(poe_oid.get("Voltage")):
                    self.set_metric(
                        id=("Interface | PoE | Voltage", None),
                        labels=[f"noc::interface::Ethernet1/0/{oid.split('.')[-1]}"],
                        value=voltage,
                        multi=True,
                        units="V",
                    )
