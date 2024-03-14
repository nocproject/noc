# ----------------------------------------------------------------------
# Eltex.LTP16N.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
from typing import List

# NOC Modules
from noc.sa.profiles.Generic.get_metrics import (
    Script as GetMetricsScript,
    metrics,
    ProfileMetricConfig,
)
from noc.core.models.cfgmetrics import MetricCollectorConfig
from noc.core.text import list_to_ranges, parse_kv


class Script(GetMetricsScript):
    name = "Eltex.LTP16N.get_metrics"

    def get_number_pon_ports(self):

        if self.capabilities["SNMP | OID | sysDescr"] == "ELTEX LTP-16N":
            N = 16
        else:
            N = 8
        return N

    splitter = re.compile(r"\s*-+\n")

    kv_map = {
        "voltage": "Interface | DOM | Voltage",
        "bias current": "Interface | DOM | Bias Current",
        "temperature": "Interface | DOM | Temperature",
        "tx power": "Interface | DOM | TxPower",
        "rx power": "Interface | DOM | RxPower",
    }

    CPE_METRICS_CONFIG = {
        "Interface | DOM | Temperature": ProfileMetricConfig(
            metric="Interface | DOM | Temperature",
            oid="",
            sla_types=[],
            scale=1,
            units="C",
        ),
        "Interface | DOM | TxPower": ProfileMetricConfig(
            metric="Interface | DOM | TxPower",
            oid="",
            sla_types=[],
            scale=1,
            units="dBm",
        ),
        "Interface | DOM | RxPower": ProfileMetricConfig(
            metric="Interface | DOM | RxPower",
            oid="",
            sla_types=[],
            scale=1,
            units="dBm",
        ),
        "Interface | DOM | Voltage": ProfileMetricConfig(
            metric="Interface | DOM | Voltage",
            oid="",
            sla_types=[],
            scale=1,
            units="VDC",
        ),
        "Interface | DOM | Bias Current": ProfileMetricConfig(
            metric="Interface | DOM | Bias Current",
            oid="",
            sla_types=[],
            scale=1,
            units="m,A",
        ),
    }

    @metrics(
        [
            "Memory | Usage",
            "Memory | Total",
        ],
        access="S",  # SNMP version
        volatile=False,
    )
    def get_memory_usage(self, metrics):
        mem_total = 7.72 * 1024 * 1024 * 1024
        mem_free = self.snmp.get("1.3.6.1.4.1.35265.1.209.1.2.2.0")
        if mem_free:
            mem_usage = 100 * (mem_total - mem_free * 1024 * 1024) / mem_total
            self.set_metric(
                id=("Memory | Total", None), value=int(mem_total), multi=True, units="byte"
            )
            self.set_metric(
                id=("Memory | Usage", None), value=int(mem_usage), multi=True, units="%"
            )

    @metrics(
        [
            "Environment | Temperature",
        ],
        access="S",  # SNMP version
        volatile=False,
    )
    def get_temperature(self, metrics):
        t = self.snmp.get("1.3.6.1.4.1.35265.1.209.1.2.19.0")
        if t:
            self.set_metric(
                id=("Environment | Temperature", None), value=int(t), multi=True, units="C"
            )

    @metrics(
        [
            "Interface | Status | Oper",
            "Interface | Status | Admin",
        ],
        access="S",  # CLI version
        volatile=False,
    )
    def get_interface_state(self, metrics):
        N = self.get_number_pon_ports()
        for iface in metrics:
            ifindex = iface.ifindex
            ilabels = iface.labels

            # Front-port
            if int(ifindex) > N:
                v = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.2.1.2.{int(ifindex)-N}")
                if v != 1:
                    v = 0
            # Pon port
            else:
                v = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.1.1.3.1.{ifindex}")
                if v == 4:
                    v = 1
                else:
                    v = 0
            self.set_metric(
                id=("Interface | Status | Oper", ilabels),
                labels=ilabels,
                value=v,
                multi=True,
            )
            self.set_metric(
                id=("Interface | Status | Admin", ilabels),
                labels=ilabels,
                value=v,
                multi=True,
            )

    @metrics(
        [
            "Interface | Speed",
        ],
        access="S",  # CLI version
        volatile=False,
    )
    def get_interface_speed(self, metrics):
        N = self.get_number_pon_ports()
        for iface in metrics:
            ifindex = iface.ifindex
            ilabels = iface.labels

            # Front-port
            if int(ifindex) > N:
                v = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.2.1.3.{int(ifindex)-N}")
            self.set_metric(
                id=("Interface | Speed", ilabels),
                labels=ilabels,
                value=v,
                units="bit/s",
                multi=True,
            )

    @metrics(
        [
            "Interface | Packets | In",
            "Interface | Packets | Out",
            "Interface | Octets | In",
            "Interface | Octets | Out",
        ],
        access="S",  # CLI version
        volatile=False,
    )
    def get_interface_packets(self, metrics):
        N = self.get_number_pon_ports()
        for iface in metrics:
            ifindex = iface.ifindex
            ilabels = iface.labels

            # Front-port
            if int(ifindex) > N:
                packets_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.1.1.3.{int(ifindex)-N}")
                packets_out = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.1.1.14.{int(ifindex)-N}")
                octets_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.1.1.2.{int(ifindex)-N}")
                octets_out = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.1.1.13.{int(ifindex)-N}")
            # Pon port
            else:
                packets_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.2.1.4.1.{ifindex}")
                packets_out = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.2.1.15.1.{ifindex}")
                octets_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.2.1.3.1.{ifindex}")
                octets_out = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.2.1.14.1.{ifindex}")
            self.set_metric(
                id=("Interface | Packets | In", ilabels),
                labels=ilabels,
                value=packets_in,
                type="counter",
                units="pps",
                multi=True,
            )
            self.set_metric(
                id=("Interface | Packets | Out", ilabels),
                labels=ilabels,
                value=packets_out,
                type="counter",
                units="pps",
                multi=True,
            )
            self.set_metric(
                id=("Interface | Octets | In", ilabels),
                labels=ilabels,
                value=octets_in,
                units="byte",
                multi=True,
            )
            self.set_metric(
                id=("Interface | Octets | Out", ilabels),
                labels=ilabels,
                value=octets_out,
                units="byte",
                multi=True,
            )

    @metrics(
        [
            "Interface | Errors | Out",
            "Interface | Errors | In",
            "Interface | Discards | Out",
            "Interface | Discards | In",
            "Interface | Errors | CRC",
            "Interface | Errors | Frame",
            "Interface | DOM | Errors | BIP | Downstream",
        ],
        access="S",  # CLI version
        volatile=False,
    )
    def get_interface_errors(self, metrics):
        N = self.get_number_pon_ports()
        for iface in metrics:
            ifindex = iface.ifindex
            ilabels = iface.labels

            # Front-port
            if int(ifindex) > N:
                errors_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.1.1.7.{int(ifindex)-N}")
                errors_out = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.1.1.18.{int(ifindex)-N}")
                errors_fcs = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.1.1.8.{int(ifindex)-N}")
                discards_in = 0
                discards_out = 0
                errors_crc = 0
            # Pon port
            else:
                errors_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.2.1.8.1.{ifindex}")
                errors_out = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.2.1.19.1.{ifindex}")
                errors_fcs = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.2.1.9.1.{ifindex}")
                discards_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.3.1.15.1.{ifindex}")
                discards_out = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.3.1.41.1.{ifindex}")
                errors_crc = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.3.1.13.1.{ifindex}")

                # For PON-port specific errors
                errors_bip = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.3.1.7.1.{ifindex}")

                self.set_metric(
                    id=("Interface | DOM | Errors | BIP | Downstream", ilabels),
                    labels=ilabels,
                    value=errors_bip,
                    type="counter",
                    units="pps",
                    multi=True,
                )

            self.set_metric(
                id=("Interface | Errors | In", ilabels),
                labels=ilabels,
                value=errors_in,
                type="counter",
                units="pps",
                multi=True,
            )
            self.set_metric(
                id=("Interface | Errors | Out", ilabels),
                labels=ilabels,
                value=errors_out,
                type="counter",
                units="pps",
                multi=True,
            )

            self.set_metric(
                id=("Interface | Discards | In", ilabels),
                labels=ilabels,
                value=discards_in,
                type="counter",
                units="pps",
                multi=True,
            )
            self.set_metric(
                id=("Interface | Discards | Out", ilabels),
                labels=ilabels,
                value=discards_out,
                type="counter",
                units="pps",
                multi=True,
            )

            self.set_metric(
                id=("Interface | Errors | CRC", ilabels),
                labels=ilabels,
                value=errors_crc,
                type="counter",
                units="pps",
                multi=True,
            )

            self.set_metric(
                id=("Interface | Errors | Frame", ilabels),
                labels=ilabels,
                value=errors_fcs,
                type="counter",
                units="pps",
                multi=True,
            )

    @metrics(
        [
            "Interface | Load | Out",
            "Interface | Load | In",
        ],
        access="S",  # CLI version
        volatile=False,
    )
    def get_interface_load(self, metrics):
        N = self.get_number_pon_ports()

        for iface in metrics:
            ifindex = iface.ifindex
            ilabels = iface.labels

            # Front-port
            if int(ifindex) > N:

                load_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.3.1.3.{int(ifindex)-N}.1")
                load_out = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.3.1.4.{int(ifindex)-N}.1")
            # Pon port
            else:
                load_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.6.1.4.1.{ifindex}.1")
                load_out = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.6.1.5.1.{ifindex}.1")
            self.set_metric(
                id=("Interface | Load | In", ilabels),
                labels=ilabels,
                value=int(load_in) * 1024,
                type="counter",
                units="bit/s",
                multi=True,
            )
            self.set_metric(
                id=("Interface | Load | Out", ilabels),
                labels=ilabels,
                value=int(load_out) * 1024,
                type="counter",
                units="bit/s",
                multi=True,
            )

    @metrics(
        [
            "Interface | Broadcast | In",
            "Interface | Broadcast | Out",
            "Interface | Multicast | In",
            "Interface | Multicast | Out",
        ],
        access="S",  # CLI version
        volatile=False,
    )
    def get_interface_broadcast_multicast(self, metrics):
        N = self.get_number_pon_ports()
        for iface in metrics:
            ifindex = iface.ifindex
            ilabels = iface.labels

            # Front-port
            if int(ifindex) > N:
                broadcast_out = self.snmp.get(
                    f"1.3.6.1.4.1.35265.1.209.1.6.1.1.17.{int(ifindex)-N}"
                )
                broadcast_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.1.1.6.{int(ifindex)-N}")
                multicast_out = self.snmp.get(
                    f"1.3.6.1.4.1.35265.1.209.1.6.1.1.16.{int(ifindex)-N}"
                )
                multicast_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.1.1.5.{int(ifindex)-N}")
            # Pon port
            else:
                broadcast_out = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.2.1.18.1.{ifindex}")
                broadcast_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.2.1.7.1.{ifindex}")
                multicast_out = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.2.1.17.1.{ifindex}")
                multicast_in = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.2.1.6.1.{ifindex}")
            self.set_metric(
                id=("Interface | Broadcast | In", ilabels),
                labels=ilabels,
                value=broadcast_out,
                type="counter",
                units="pps",
                multi=True,
            )
            self.set_metric(
                id=("Interface | Broadcast | Out", ilabels),
                labels=ilabels,
                value=broadcast_in,
                type="counter",
                units="pps",
                multi=True,
            )
            self.set_metric(
                id=("Interface | Multicast | In", ilabels),
                labels=ilabels,
                value=multicast_out,
                units="byte",
                multi=True,
            )
            self.set_metric(
                id=("Interface | Multicast | Out", ilabels),
                labels=ilabels,
                value=multicast_in,
                units="byte",
                multi=True,
            )

    @metrics(
        [
            "Interface | DOM | Temperature",
            "Interface | DOM | Voltage",
            "Interface | DOM | Bias Current",
            "Interface | DOM | TxPower",
        ],
        access="S",  # CLI version
        volatile=False,
    )
    def get_interface_dom(self, metrics):
        N = self.get_number_pon_ports()
        for iface in metrics:
            ifindex = iface.ifindex
            ilabels = iface.labels

            # Front-port
            if int(ifindex) > N:
                temperature = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.6.1.9.{int(ifindex)-N}")
                voltage = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.6.1.10.{int(ifindex)-N}")
                current = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.6.1.11.{int(ifindex)-N}")
                tx_power = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.6.1.12.{int(ifindex)-N}")
            # Pon port
            else:
                temperature = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.1.1.8.1.{ifindex}")
                voltage = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.1.1.9.1.{ifindex}")
                current = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.1.1.10.1.{ifindex}")
                tx_power = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.1.1.11.1.{ifindex}")

            if temperature == 32766:
                temperature = 0
            if voltage == 32766:
                voltage = 0
            else:
                voltage = voltage * 0.01
            if current == 32766:
                current = 0
            else:
                current = current * 0.000000001
            if tx_power == 32766:
                tx_power = 0

            self.set_metric(
                id=("Interface | DOM | Temperature", ilabels),
                labels=ilabels,
                value=temperature,
                type="gauge",
                units="C",
                multi=True,
            )
            self.set_metric(
                id=("Interface | DOM | Voltage", ilabels),
                labels=ilabels,
                value=voltage,
                type="gauge",
                units="VDC",
                multi=True,
            )
            self.set_metric(
                id=("Interface | DOM | Bias Current", ilabels),
                labels=ilabels,
                value=current,
                type="gauge",
                units="A",
                multi=True,
            )
            self.set_metric(
                id=("Interface | DOM | TxPower", ilabels),
                labels=ilabels,
                value=tx_power,
                type="gauge",
                units="dBm",
                multi=True,
            )

    def collect_cpe_metrics(self, metrics: List[MetricCollectorConfig]):
        """
        Collect metrics on client side(ONT).
        """
        ont_ifaces = defaultdict(dict)
        ts = self.get_ts()
        # Group metric by port
        for probe in metrics:
            hints = probe.get_hints()
            port, ont_id = hints["local_id"].split("/")
            ont_ifaces[port][ont_id] = probe
        if not ont_ifaces:
            return
        for iface, ont_ids in ont_ifaces.items():
            port = iface
            try:
                c = self.cli(
                    f"show interface ont {port}/{list_to_ranges([int(x) for x in ont_ids])} laser"
                )
            except self.CLISyntaxError:
                raise NotImplementedError
            parts = self.splitter.split(c)
            parts = parts[1:]
            while len(parts) > 1:
                (header, body), parts = parts[:2], parts[2:]
                if len(body) <= 100:
                    continue
                data = parse_kv(self.kv_map, body)
                cpe_id = header.split("[")[-1].split("]")[0].lower()
                port, ont_id = cpe_id.split("/")
                if ont_id not in ont_ids:
                    continue
                probe = ont_ids[ont_id]
                for m, mc in self.CPE_METRICS_CONFIG.items():
                    if mc.metric not in data or data[mc.metric] == "n/a" or m not in probe.metrics:
                        continue
                    self.set_metric(
                        id=probe.cpe,
                        cpe=probe.cpe,
                        metric=m,
                        value=float(data[mc.metric].split()[0]),
                        ts=ts,
                        labels=probe.labels + ["noc::interface::0"],
                        multi=True,
                        type="gauge",
                        scale=mc.scale,
                        units=mc.units,
                    )
