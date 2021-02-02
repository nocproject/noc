# ---------------------------------------------------------------------
# Sumavision.IPQAM.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "Sumavision.IPQAM.get_metrics"

    @metrics(
        ["Interface | Load | In", "Interface | Status | Admin", "Interface | Status | Oper"],
        has_capability="DB | Interfaces",
        volatile=True,
        access="S",  # SNMP version
    )
    def get_interface_metrics(self, metrics):
        for metric in metrics:
            ifname = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.3008.4.2.1.11.1.1.%s" % metric.ifindex)
            istatus = self.snmp.get(
                "1.3.6.1.4.1.32285.2.2.10.3008.4.2.1.10.1.1.%s" % metric.ifindex
            )
            load = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.3008.4.5.1.3.1.%s" % metric.ifindex)
            self.set_metric(
                id=("Interface | Status | Admin", ["", "", "", ifname]),
                value=1 if istatus not in ["Shut Down", "linkError"] else 0,
                type="gauge",
                scale=1,
            )
            self.set_metric(
                id=("Interface | Status | Oper", ["", "", "", ifname]),
                value=1 if istatus not in ["Shut Down", "Link Error"] else 0,
                type="gauge",
                scale=1,
            )
            self.set_metric(
                id=("Interface | Load | In", ["", "", "", ifname]),
                value=float(load.rstrip("Mbps")),
                type="gauge",
                scale=1000000,
            )

    @metrics(
        [
            "Multicast | Channel | Bandwidth | Used",
        ],
        has_capability="DB | Interfaces",
        volatile=True,
        access="S",  # SNMP version
    )
    def get_channel_bandwidth_u_metrics(self, metrics):
        for metric in metrics:
            used_bandwidth = self.snmp.get(
                "1.3.6.1.4.1.32285.2.2.10.3008.5.3.1.18.1.1.%s" % metric.ifindex
            )
            self.set_metric(
                id=(
                    "Multicast | Channel | Bandwidth | Used",
                    ["", "", "", "1/1.%s" % metric.ifindex],
                ),
                path=(["", "1/1.%s" % metric.ifindex]),
                value=float(used_bandwidth.rstrip("Mbps")),
                type="gauge",
                scale=100000,
            )

    @metrics(
        [
            "Multicast | Channel | Bandwidth | Percent",
        ],
        has_capability="DB | Interfaces",
        volatile=True,
        access="S",  # SNMP version
    )
    def get_channel_bandwidth_p_metrics(self, metrics):
        for metric in metrics:
            used_bandwidth = self.snmp.get(
                "1.3.6.1.4.1.32285.2.2.10.3008.5.3.1.18.1.1.%s" % metric.ifindex
            )
            capacity_bandwidth = self.snmp.get(
                "1.3.6.1.4.1.32285.2.2.10.3008.5.3.1.19.1.1.%s" % metric.ifindex
            )
            value = (100 / float(capacity_bandwidth.rstrip("Mbps"))) * float(
                used_bandwidth.rstrip("Mbps")
            )
            self.set_metric(
                id=(
                    "Multicast | Channel | Bandwidth | Percent",
                    ["", "", "", "1/1.%s" % metric.ifindex],
                ),
                path=(["", "1/1.%s" % metric.ifindex]),
                value=int(value),
                type="gauge",
                scale=1,
            )

    @metrics(
        ["Multicast | Channel | Group | Count"],
        has_capability="DB | Interfaces",
        volatile=True,
        access="S",  # SNMP version
    )
    def get_channel_udp_metrics(self, metrics):
        for metric in metrics:
            udp_ports = self.snmp.get(
                "1.3.6.1.4.1.32285.2.2.10.3008.5.3.1.17.1.1.%s" % metric.ifindex
            )
            self.set_metric(
                id=("Multicast | Channel | Group | Count", ["", "", "", "1/1.%s" % metric.ifindex]),
                path=(["", "1/1.%s" % metric.ifindex]),
                value=udp_ports,
                type="gauge",
                scale=1,
            )

    @metrics(
        ["Multicast | Group | Status"],
        has_capability="DB | Interfaces",
        volatile=True,
        access="S",  # SNMP version
    )
    def get_group_metrics(self, metrics):

        for metric in metrics:
            channel, index = int(str(metric.ifindex)[0]), int(str(metric.ifindex)[1:])
            mname = self.snmp.get(
                "1.3.6.1.4.1.32285.2.2.10.3008.5.6.1.5.1.1.%s.%s" % (channel, index)
            )
            try:
                minname = self.snmp.get(
                    "1.3.6.1.4.1.32285.2.2.10.3008.4.6.1.8.1.1.%s.%s" % (channel, index)
                )
                if minname and mname == minname:
                    m_ostatus = 1
            except self.snmp.SNMPError:
                m_ostatus = -1

            self.set_metric(
                id=("Multicast | Group | Status", ["", "", "", mname]),
                path=([mname, "1/1.%s" % channel]),
                value=m_ostatus,
                type="gauge",
                scale=1,
            )

    @metrics(
        ["Multicast | Group | Bitrate | In"],
        has_capability="DB | Interfaces",
        volatile=True,
        access="S",  # SNMP version
    )
    def get_group_bitrate_in_metrics(self, metrics):
        for metric in metrics:
            channel, index = int(str(metric.ifindex)[0]), int(str(metric.ifindex)[1:])
            mname = self.snmp.get(
                "1.3.6.1.4.1.32285.2.2.10.3008.5.6.1.5.1.1.%s.%s" % (channel, index)
            )
            try:
                input = self.snmp.get(
                    "1.3.6.1.4.1.32285.2.2.10.3008.4.6.1.18.1.1.%s.%s" % (channel, index)
                )
                input = float(input.rstrip("Mbps"))
            except self.snmp.SNMPError:
                input = 0
            self.set_metric(
                id=("Multicast | Group | Bitrate | In", ["", "", "", mname]),
                path=([mname, "1/1.%s" % channel]),
                value=input,
                type="gauge",
                scale=100000,
            )

    @metrics(
        ["Multicast | Group | Bitrate | Out"],
        has_capability="DB | Interfaces",
        volatile=True,
        access="S",  # SNMP version
    )
    def get_group_bitrate_out_metrics(self, metrics):
        for metric in metrics:
            channel, index = int(str(metric.ifindex)[0]), int(str(metric.ifindex)[1:])
            mname = self.snmp.get(
                "1.3.6.1.4.1.32285.2.2.10.3008.5.6.1.5.1.1.%s.%s" % (channel, index)
            )
            try:
                input = self.snmp.get(
                    "1.3.6.1.4.1.32285.2.2.10.3008.5.6.1.24.1.1.%s.%s" % (channel, index)
                )
                input = float(input.rstrip("Mbps"))
            except self.snmp.SNMPError:
                input = 0
            self.set_metric(
                id=("Multicast | Group | Bitrate | Out", ["", "", "", mname]),
                path=([mname, "1/1.%s" % channel]),
                value=input,
                type="gauge",
                scale=100000,
            )
