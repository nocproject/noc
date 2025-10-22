# ---------------------------------------------------------------------
# ZTE.ZXDSL98xx.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "ZTE.ZXDSL98xx.get_interfaces"
    interface = IGetInterfaces

    rx_ip = re.compile(
        r"^-{70,}\s*\n"
        r"(?P<subs>(^\s+\d+\S+\s+\d+\S+\s+\d+\s+active\s*\n)+)"
        r"^\s*\n"
        r"^In band\s*\n"
        r"^-------\s*\n"
        r"^MAC address\s+: (?P<inband_mac>\S+)\s*\n"
        r"^\s*\n"
        r"^Out of band\s*\n"
        r"^-----------\s*\n"
        r"^IP address\s+: (?P<ip>\S+)\s*\n"
        r"^Netmask\s+: (?P<mask>\S+)\s*\n"
        r"^MAC address\s+: (?P<outband_mac>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_ip_9806h = re.compile(
        r"^\s+(?P<ip>\d+\S+\d+)\s+(?P<mask>\d+\S+\d+)\s+"
        r"(?P<vlan_id>\d+)\s+(?P<ifname>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_ip_host = re.compile(
        r"^Host IP address\s+: (?P<ip>\S+)\s*\n^Host IP mask\s+: (?P<mask>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_sub = re.compile(r"^\s+(?P<ip>\d+\S+)\s+(?P<mask>\d+\S+)\s+(?P<vlan_id>\d+)", re.MULTILINE)
    rx_card = re.compile(
        r"^(?P<slot>\d+)\s+\S+\s+\S+\s+\S+\s+(?P<ports>\d+)\s+\S+\s*\n", re.MULTILINE
    )
    rx_card_9806h = re.compile(
        r"^\s+(?P<slot>\d+)\s+\d+\s+\S+\s+(?P<ports>\d+)\s+\d+\s+\S+\s+Inservice\s*\n", re.MULTILINE
    )
    rx_ethernet = re.compile(
        r"^Interface\s+: .+\n"
        r"^name\s+: .+\n"
        r"^Pvid\s+: (?P<pvid>\d+)\s*\n"
        r"^AdminStatus\s+: (?P<admin_status>\S+)\s+LinkStatus\(Eth\)\s+: (?P<oper_status>\S+)\s*\n"
        r"^ifType\s+: Ethernet\s+.+\n"
        r"^ifMtu\s+: (?P<mtu>\d+)\s+.+\n",
        re.MULTILINE,
    )
    rx_if_admin_status = re.compile(r"AdminStatus\s+:\s+(?P<status>\S+)")
    rx_if_oper_status = re.compile(r"LinkStatus\s+:\s+(?P<status>\S+)")
    rx_ether_type = re.compile(r"IfType\s+:\s+ETH_PORT_TYPE")
    rx_adsl_type = re.compile(r"IfType\s+:\s+ADSL_PORT_TYPE")
    rx_ether_vlan = re.compile(
        r"^Interface\s+: \S+\s*\n"
        r"^Tagged VLAN list\s+:(?P<tagged>.*)\n"
        r"^Untagged VLAN list\s+:(?P<untagged>.*)\n",
        re.MULTILINE,
    )
    # Do not optimize this.
    rx_adsl = re.compile(
        r"^Interface\s+: .+\n"
        r"^name\s+: .+\n"
        r"Pvid PVC1\s+: (?P<pvid1>\d+)\s+Pvid PVC2\s+: (?P<pvid2>\d+)\s*\n"
        r"Pvid PVC3\s+: (?P<pvid3>\d+)\s+Pvid PVC4\s+: (?P<pvid4>\d+)\s*\n"
        r"Pvid PVC5\s+: (?P<pvid5>\d+)\s+Pvid PVC6\s+: (?P<pvid6>\d+)\s*\n"
        r"Pvid PVC7\s+: (?P<pvid7>\d+)\s+Pvid PVC8\s+: (?P<pvid8>\d+)\s*\n"
        r"^\s*\n"
        r"^AdminStatus\s+: (?P<admin_status>\S+)\s+LinkStatus\(ADSL\)\s+: (?P<oper_status>\S+)\s*\n"
        r"^ifType\s+: ADSL\s+ifMtu\s+: (?P<mtu>\d+)\s+.+\n",
        re.MULTILINE,
    )
    # Do not optimize this.
    rx_pvc = re.compile(
        r"^\d+/\d+\s+PVC1\s+(?P<vpi1>\d+)\s+(?P<vci1>\d+).*\n"
        r"^\d+/\d+\s+PVC2\s+(?P<vpi2>\d+)\s+(?P<vci2>\d+).*\n"
        r"^\d+/\d+\s+PVC3\s+(?P<vpi3>\d+)\s+(?P<vci3>\d+).*\n"
        r"^\d+/\d+\s+PVC4\s+(?P<vpi4>\d+)\s+(?P<vci4>\d+).*\n"
        r"^\d+/\d+\s+PVC5\s+(?P<vpi5>\d+)\s+(?P<vci5>\d+).*\n"
        r"^\d+/\d+\s+PVC6\s+(?P<vpi6>\d+)\s+(?P<vci6>\d+).*\n"
        r"^\d+/\d+\s+PVC7\s+(?P<vpi7>\d+)\s+(?P<vci7>\d+).*\n"
        r"^\d+/\d+\s+PVC8\s+(?P<vpi8>\d+)\s+(?P<vci8>\d+).*\n",
        re.MULTILINE,
    )
    rx_pvc_9806h = re.compile(
        r"^\s*(?P<port>\d+)\s+(?P<pvcid>\d+)\s+(?P<vpi>\d+)\s+(?P<vci>\d+)\s+"
        r"(?P<pvid>\d+)\s+\S+\s+(?P<state>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        interfaces = []
        v = self.cli("show ip subnet")
        match = self.rx_ip.search(v)
        if match:
            i = {
                "name": "inband",
                "type": "SVI",
                "mac": match.group("inband_mac"),
                "subinterfaces": [],
            }
            sub_number = 0
            for match1 in self.rx_sub.finditer(match.group("subs")):
                ip = match1.group("ip")
                mask = match1.group("mask")
                ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
                sub = {
                    "name": "inband%s" % sub_number,
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [ip_address],
                    "vlan_ids": [match1.group("vlan_id")],
                }
                sub_number = sub_number + 1
                i["subinterfaces"] += [sub]
            interfaces += [i]
            ip = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
            i = {
                "name": "outb",
                "type": "SVI",
                "mac": match.group("outband_mac"),
                "subinterfaces": [
                    {"name": "outband", "enabled_afi": ["IPv4"], "ipv4_addresses": [ip_address]}
                ],
            }
        else:
            match = self.rx_ip_9806h.search(v)
            if match:
                ip = match.group("ip")
                mask = match.group("mask")
                ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
                i = {
                    "name": match.group("ifname"),
                    "type": "SVI",
                    "subinterfaces": [
                        {
                            "name": match.group("ifname"),
                            "enabled_afi": ["IPv4"],
                            "ipv4_addresses": [ip_address],
                            "vlan_ids": [match.group("vlan_id")],
                        }
                    ],
                }
                interfaces += [i]
            else:
                raise self.NotSupportedError()
        try:
            v = self.cli("show ip host")
            match = self.rx_ip_host.search(v)
            ip = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
            i = {
                "name": "host",
                "type": "management",
                "subinterfaces": [
                    {"name": "host", "enabled_afi": ["IPv4"], "ipv4_addresses": [ip_address]}
                ],
            }
            interfaces += [i]
        except self.CLISyntaxError:
            pass
        rx_card = self.rx_card_9806h if self.is_9806h else self.rx_card
        for match in rx_card.finditer(self.cli("show card")):
            slot = match.group("slot")
            ports = match.group("ports")
            if ports == 0:
                continue
            for port_n in range(int(ports)):
                ifname = "%s/%s" % (slot, port_n + 1)
                try:
                    v = self.cli("show interface %s" % ifname)
                except self.CLISyntaxError:
                    continue
                match = self.rx_ethernet.search(v)
                if match:
                    i = {
                        "name": ifname,
                        "type": "physical",
                        "admin_status": match.group("admin_status") == "enable",
                        "oper_status": match.group("oper_status") == "up",
                        "hints": [
                            "noc::topology::direction::nni",
                            "technology::ethernet::1000base",
                        ],
                        "subinterfaces": [
                            {
                                "name": ifname,
                                "enabled_afi": ["BRIDGE"],
                                "mtu": match.group("mtu"),
                                "admin_status": match.group("admin_status") == "enable",
                                "oper_status": match.group("oper_status") == "up",
                            }
                        ],
                    }
                    interfaces += [i]
                match = self.rx_adsl.search(v)
                if match:
                    i = {
                        "name": ifname,
                        "type": "physical",
                        "admin_status": match.group("admin_status") == "enable",
                        "oper_status": match.group("oper_status") == "up",
                        "hints": ["technology::dsl::adsl"],
                        "subinterfaces": [],
                    }
                    v = self.cli("show atm pvc interface %s" % ifname)
                    match1 = self.rx_pvc.search(v)
                    i["subinterfaces"] = [
                        {
                            "name": "%s/%s" % (ifname, "1"),
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "mtu": match.group("mtu"),
                            "vlan_ids": [match.group("pvid1")],
                            "vpi": match1.group("vpi1"),
                            "vci": match1.group("vci1"),
                        },
                        {
                            "name": "%s/%s" % (ifname, "2"),
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "mtu": match.group("mtu"),
                            "vlan_ids": [match.group("pvid2")],
                            "vpi": match1.group("vpi2"),
                            "vci": match1.group("vci2"),
                        },
                        {
                            "name": "%s/%s" % (ifname, "3"),
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "mtu": match.group("mtu"),
                            "vlan_ids": [match.group("pvid3")],
                            "vpi": match1.group("vpi3"),
                            "vci": match1.group("vci3"),
                        },
                        {
                            "name": "%s/%s" % (ifname, "4"),
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "mtu": match.group("mtu"),
                            "vlan_ids": [match.group("pvid4")],
                            "vpi": match1.group("vpi4"),
                            "vci": match1.group("vci4"),
                        },
                        {
                            "name": "%s/%s" % (ifname, "5"),
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "mtu": match.group("mtu"),
                            "vlan_ids": [match.group("pvid5")],
                            "vpi": match1.group("vpi5"),
                            "vci": match1.group("vci5"),
                        },
                        {
                            "name": "%s/%s" % (ifname, "6"),
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "mtu": match.group("mtu"),
                            "vlan_ids": [match.group("pvid6")],
                            "vpi": match1.group("vpi6"),
                            "vci": match1.group("vci6"),
                        },
                        {
                            "name": "%s/%s" % (ifname, "7"),
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "mtu": match.group("mtu"),
                            "vlan_ids": [match.group("pvid7")],
                            "vpi": match1.group("vpi7"),
                            "vci": match1.group("vci7"),
                        },
                        {
                            "name": "%s/%s" % (ifname, "8"),
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "mtu": match.group("mtu"),
                            "vlan_ids": [match.group("pvid8")],
                            "vpi": match1.group("vpi8"),
                            "vci": match1.group("vci8"),
                        },
                    ]
                    interfaces += [i]
                match = self.rx_ether_type.search(v)
                if match:
                    match = self.rx_if_admin_status.search(v)
                    admin_status = match.group("status") == "enable"
                    match = self.rx_if_oper_status.search(v)
                    oper_status = match.group("status") == "up"
                    i = {
                        "name": ifname,
                        "type": "physical",
                        "admin_status": admin_status,
                        "hints": [
                            "noc::topology::direction::nni",
                            "technology::ethernet::1000base",
                        ],
                        "oper_status": oper_status,
                        "subinterfaces": [
                            {
                                "name": ifname,
                                "enabled_afi": ["BRIDGE"],
                                "admin_status": admin_status,
                                "oper_status": oper_status,
                            }
                        ],
                    }
                    v = self.cli("show interface %s vlan-config" % ifname)
                    match = self.rx_ether_vlan.search(v)
                    if match.group("tagged").strip():
                        i["subinterfaces"][0]["tagged_vlans"] = self.expand_rangelist(
                            match.group("tagged").strip()
                        )
                    if match.group("tagged").strip():
                        i["subinterfaces"][0]["tagged_vlans"] = self.expand_rangelist(
                            match.group("tagged").strip()
                        )

                    interfaces += [i]
                match = self.rx_adsl_type.search(v)
                if match:
                    match = self.rx_if_admin_status.search(v)
                    admin_status = match.group("status") == "enable"
                    match = self.rx_if_oper_status.search(v)
                    oper_status = match.group("status") == "up"
                    i = {
                        "name": ifname,
                        "type": "physical",
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "hints": ["technology::dsl::adsl"],
                        "subinterfaces": [],
                    }
                    v = self.cli("show atm vc %s" % ifname)
                    for match in self.rx_pvc_9806h.finditer(v):
                        sub = {
                            "name": "%s/%s" % (ifname, match.group("pvcid")),
                            "admin_status": True,
                            "oper_status": match.group("state") == "enable",
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "vlan_ids": [match.group("pvid")],
                            "vpi": match.group("vpi"),
                            "vci": match.group("vci"),
                        }
                        i["subinterfaces"] += [sub]

                    interfaces += [i]

        return [{"interfaces": interfaces}]
