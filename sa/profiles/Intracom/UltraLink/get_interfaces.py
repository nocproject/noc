# ----------------------------------------------------------------------
# Intracom.UltraLink.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Intracom.UltraLink.get_interfaces"
    interface = IGetInterfaces

    rx_modem_link = re.compile(r"\s+Link Status : (?P<status>\S+)")
    rx_eth_port = re.compile(
        r"\s+Ethernet Interface : (?P<ifname>\S+)\n"
        r"\s+Ethernet Interface Type : \S+\n"
        r"(?:\s+SFP Existence Status : \S+\n)?"
        r"\s+Link Status : (?P<oper>\S+)\n"
        r"\s+Admin Status : (?P<admin>\S+)\n"
        r"(?:\s+Rx Loss of Signal Status : \S+\n"
        r"\s+ Tx Fault Indication Status : \S+\n)?"
        r"\s+Speed : \S+\n"
        r"\s+Duplex Mode : \S+\n"
        r"\s+Negotiation Mode : \S+\n"
        r"\s+Ethernet Port MAC Address : (?P<mac>\S+)"
    )
    rx_ipaddr = re.compile(
        r"\s+Bridge Mng MAC Address : (?P<mac>\S+)\n"
        r"\s+Inband Mng IP Address : (?P<ipaddr>\S+)\n"
        r"\s+Inband Mng Net Mask : (?P<mask>\S+)\n"
        r"\s+Inband Mng Vlan Id : (?P<vid>\d+)\n"
    )
    rx_vlanport = re.compile(r"\s+(?P<port>\S+)\s+(?P<vid>\d+)\s+\S*")
    rx_bridgeport = re.compile(
        r"(?P<port>\S+)\s+[CS]VLAN Mode Port\s+(?P<pvid>\d+)\s+\d+\s+"
        r"(?P<frame_type>\S+)\s+(?:Incoming C Tag|Default)\s+\S+\s+\S+"
    )

    def execute_cli(self, **kwargs):
        ifaces = []
        port_vlan = defaultdict(list)
        port_pvid = defaultdict()
        # VLANs
        cli = self.cli("get bridge vlanport")
        for match in self.rx_vlanport.finditer(cli):
            port_vlan[match.group("port")] += [match.group("vid")]
        cli = self.cli("get bridge l2port")
        for match in self.rx_bridgeport.finditer(cli):
            if "Untagged" in match.group("frame_type"):
                port_pvid[match.group("port")] = match.group("pvid")
        # Ethernet ports
        cli = self.cli("get ethernet state")
        for match in self.rx_eth_port.finditer(cli):
            ifc = {
                "name": match.group("ifname"),
                "admin_status": match.group("admin"),
                "oper_status": match.group("oper"),
                "type": "physical",
                "mac": match.group("mac"),
                "subinterfaces": [
                    {
                        "name": match.group("ifname"),
                        "admin_status": match.group("admin"),
                        "oper_status": match.group("oper"),
                        "mac": match.group("mac"),
                        "enabled_afi": ["BRIDGE"],
                        "tagged_vlans": port_vlan[
                            match.group("ifname")
                        ],  # @todo: ES for QinQ support
                    }
                ],
            }
            if match.group("ifname") in port_pvid:
                ifc["subinterfaces"][0]["untagged_vlan"] = port_pvid[match.group("ifname")]
            ifaces += [ifc]
        # @todo: LAG ports
        # Modem port
        cli = self.cli("get modem remoteinfo")
        modem_link = self.rx_modem_link.search(cli).group("status")
        ifc = {
            "name": "modem",
            "admin_status": True,
            "oper_status": modem_link == "Locked",
            "type": "physical",
            "subinterfaces": [
                {
                    "name": "modem",
                    "enabled_afi": ["BRIDGE"],
                    "admin_status": True,
                    "oper_status": modem_link == "Locked",
                    "tagged_vlans": port_vlan["modem"],  # @todo: ES for QinQ support
                }
            ],
        }
        if "modem" in port_pvid:
            ifc["subinterfaces"][0]["untagged_vlan"] = port_pvid["modem"]
        ifaces += [ifc]
        # Management
        cli = self.cli("get system info")
        match = self.rx_ipaddr.search(cli)
        ipaddr = match.group("ipaddr")
        mask = match.group("mask")
        ip = IPv4(ipaddr, mask)
        ifaces += [
            {
                "name": "Inband Mng",
                "admin_status": True,
                "oper_status": True,
                "type": "SVI",
                "mac": match.group("mac"),
                "subinterfaces": [
                    {
                        "name": "Inband Mng",
                        "admin_status": True,
                        "oper_status": True,
                        "mac": match.group("mac"),
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [ip],
                        "vlan_ids": [match.group("vid")],
                    }
                ],
            }
        ]

        return [{"interfaces": ifaces}]
