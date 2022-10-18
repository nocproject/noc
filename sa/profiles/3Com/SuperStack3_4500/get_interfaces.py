# ----------------------------------------------------------------------
# 3Com.SuperStack3_4500.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "3Com.SuperStack3_4500.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^\s*(?P<iface>\S+) current state\s*:\s*(?P<status>(UP|DOWN|ADMINISTRATIVELY DOWN))\s*\n",
        re.MULTILINE,
    )

    rx_descr = re.compile(r"^\s*Description\s*:(?P<description>.+)\s*\n", re.MULTILINE)
    rx_mac = re.compile(r"Hardware address is (?P<mac>\S+)")
    rx_mtu = re.compile(
        r"^\s*The Maximum (?:Frame Length|Transmit Unit) is (?P<mtu>\d+)", re.MULTILINE
    )
    rx_pvid = re.compile(r"^\s*PVID: (?P<pvid>\d+)", re.MULTILINE)
    rx_type = re.compile(r"^\s*Port link-type: (?P<type>access|trunk|stack)", re.MULTILINE)
    rx_tagged = re.compile(r"^\s*VLAN permitted: (?P<tagged>.+)\s*\n", re.MULTILINE)
    rx_tagged2 = re.compile(r"^\s*Tagged(?:\s+VLAN ID ): (?P<tagged>.+)\s*\n", re.MULTILINE)
    rx_ip = re.compile(r"^\s*Internet Address is (?P<ip>\S+) Primary\s*\n", re.MULTILINE)

    def execute_cli(self):
        interfaces = []
        ifaces = self.cli("display interface", cached=True)
        for i in ifaces.split("\n\n"):
            match = self.rx_iface.search(i)
            if match:
                ifname = match.group("iface")
                o_stat = match.group("status") == "UP"
                a_stat = match.group("status") != "ADMINISTRATIVELY DOWN"
                iface = {
                    "name": ifname,
                    "type": self.profile.get_interface_type(ifname),
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "subinterfaces": [],
                }
                sub = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                }
                match = self.rx_descr.search(i)
                if match:
                    iface["description"] = match.group("description").strip()
                match = self.rx_mac.search(i)
                if match:
                    iface["mac"] = match.group("mac")
                    sub["mac"] = match.group("mac")
                match = self.rx_mtu.search(i)
                if match:
                    iface["mtu"] = match.group("mtu")
                    sub["mtu"] = match.group("mtu")
                match = self.rx_type.search(i)
                if match:
                    sub["enabled_afi"] = ["BRIDGE"]
                    if match.group("type") in ["trunk", "stack"]:
                        match = self.rx_tagged.search(i)
                        if match:
                            tagged = match.group("tagged")
                        else:
                            match = self.rx_tagged2.search(i)
                            tagged = match.group("tagged")
                        tagged = tagged.replace("(default vlan)", "")
                        tagged = tagged.replace("all", "1-4094")
                        sub["tagged_vlans"] = self.expand_rangelist(tagged)
                    match = self.rx_pvid.search(i)
                    sub["untagged_vlan"] = match.group("pvid")
                match = self.rx_ip.search(i)
                if match:
                    sub["enabled_afi"] = ["IPv4"]
                    sub["ipv4_addresses"] = [match.group("ip")]
                if ifname.startswith("Vlan-interface"):
                    vlan_id = ifname[14:]
                    sub["vlan_ids"] = vlan_id
                iface["subinterfaces"] = [sub]
                interfaces += [iface]

        return [{"interfaces": interfaces}]
