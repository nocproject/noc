# ---------------------------------------------------------------------
# Ubiquiti.AirOS.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.core.mib import mib


class Script(GetMetricsScript):
    name = "Ubiquiti.AirOS.get_metrics"

    @metrics(["Memory | Total"], volatile=False, access="S")  # SNMP version
    def get_memory_total(self, metrics):
        oid_total = "1.3.6.1.4.1.10002.1.1.1.1.1.0"
        value = self.snmp.get(oid_total)

        if value:
            self.set_metric(
                id=("Memory | Total", None), metric="Memory | Total", value=int(value), units="byte"
            )

    @metrics(["Memory | Usage"], volatile=False, access="S")  # SNMP version
    def get_memory_usage(self, metrics):
        oid_total = "1.3.6.1.4.1.10002.1.1.1.1.1.0"
        oid_usage = "1.3.6.1.4.1.10002.1.1.1.1.2.0"
        memory_total = self.snmp.get(oid_total)
        value = self.snmp.get(oid_usage) * 100 / memory_total

        if value:
            self.set_metric(
                id=("Memory | Usage", None),
                metric="Memory | Usage",
                value=round(float(value)),
                units="%",
            )

    @metrics(["CPU | Usage"], volatile=False, access="S")  # SNMP version
    def get_cpu_usage(self, metrics):

        # 1.3.6.1.4.1.41112.1.4.8.3 for SNMP, but OID not working on devices
        # model "M2 Titanium"
        result = self.snmp.get("1.3.6.1.4.1.41112.1.4.8.3")
        if result:
            self.set_metric(id=("CPU | Usage", None), value=result, units="%")

    @metrics(["Environment | Temperature"], volatile=False, access="S")  # SNMP version
    def get_temperature(self, metrics):

        # 1.3.6.1.4.1.41112.1.4.8.4.0 for SNMP, but OID not working on devices
        # model "M2 Titanium"
        value = self.snmp.get("1.3.6.1.4.1.41112.1.4.8.4.0")
        if value:
            self.set_metric(id=("Environment | Temperature", None), value=value, units="C")

    @metrics(["Object | MAC | TotalUsed"], volatile=False, access="S")  # SNMP version
    def get_mac_count(self, metrics):
        count = 0
        for _, mac in self.snmp.getnext("1.3.6.1.4.1.41112.1.4.7.1.1"):
            if mac:
                count += 1
        if count:
            self.set_metric(id=("Object | MAC | TotalUsed", None), value=count)

    @metrics(
        [
            "Interface | Discards | In",
            "Interface | Discards | Out",
            "Interface | Errors | In",
            "Interface | Errors | Out",
        ],
        volatile=False,
        access="S",
    )  # SNMP version
    def get_iface_metrics(self, metrics):
        metrics_indexes = [
            ("discards_in", 13),
            ("discards_out", 19),
            ("errors_in", 14),
            ("errors_out", 20),
        ]
        base_oid = "1.3.6.1.2.1.2.2.1"
        iface_list = []
        for iface in self.snmp.getnext(mib["IF-MIB::ifDescr"]):
            iface_list.append(iface[1])
        for metric in metrics:
            oids = {name: f"{base_oid}.{metrics_index}" for name, metrics_index in metrics_indexes}

            if oids["discards_in"]:
                for oid, value in self.snmp.getnext(oids.get("discards_in")):
                    iface = iface_list[int(oid[-1]) - 1]
                    if value:
                        self.set_metric(
                            id=("Interface | Discards | In", None),
                            metric="Interface | Discards | In",
                            labels=[f"noc::interface::{iface}"],
                            value=int(value),
                            multi=True,
                            units="pkt",
                        )

            if oids["discards_out"]:
                for oid, value in self.snmp.getnext(oids.get("discards_out")):
                    iface = iface_list[int(oid[-1]) - 1]
                    if value:
                        self.set_metric(
                            id=("Interface | Discards | Out", None),
                            metric="Interface | Discards | Out",
                            labels=[f"noc::interface::{iface}"],
                            value=int(value),
                            multi=True,
                            units="pkt",
                        )

            if oids["errors_in"]:
                for oid, value in self.snmp.getnext(oids.get("errors_in")):
                    iface = iface_list[int(oid[-1]) - 1]
                    if value:
                        self.set_metric(
                            id=("Interface | Errors | In", None),
                            metric="Interface | Errors | In",
                            labels=[f"noc::interface::{iface}"],
                            value=int(value),
                            multi=True,
                        )

            if oids["errors_out"]:
                for oid, value in self.snmp.getnext(oids.get("errors_out")):
                    iface = iface_list[int(oid[-1]) - 1]
                    if value:
                        self.set_metric(
                            id=("Interface | Errors | Out", None),
                            metric="Interface | Errors | Out",
                            labels=[f"noc::interface::{iface}"],
                            value=int(value),
                            multi=True,
                        )

    @metrics(
        ["Radio | TxPower", "Radio | Level | Signal", "Radio | Level | Noise"],
        volatile=False,
        access="S",
    )  # SNMP version
    def get_radio_metrics(self, metrics):
        iface, units = "ath0", "dBm"
        tx_power = self.snmp.get("1.3.6.1.4.1.41112.1.4.1.1.6.1")
        signal = self.snmp.get("1.3.6.1.4.1.41112.1.4.5.1.5.1")
        noise = self.snmp.get("1.3.6.1.4.1.41112.1.4.5.1.8.1")

        if tx_power:
            self.set_metric(
                id=("Radio | TxPower", None),
                labels=[f"noc::interface::{iface}"],
                value=tx_power,
                units=units,
            )
        if signal:
            self.set_metric(
                id=("Radio | Level | Signal", None),
                labels=[f"noc::interface::{iface}"],
                value=signal,
                units=units,
            )
        if noise:
            self.set_metric(
                id=("Radio | Level | Noise", None),
                labels=[f"noc::interface::{iface}"],
                value=noise,
                units=units,
            )
