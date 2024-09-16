# ---------------------------------------------------------------------
# Zyxel.DSLAM.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Zyxel.DSLAM.get_interfaces"
    interface = IGetInterfaces

    rx_sub_pvc = re.compile(
        r"^\s*(?P<sub>\d+)\s+(?P<vpi>\d+)\s+(?P<vci>\d+)\s+(?P<pvid>\S+)\s+", re.MULTILINE
    )
    rx_ipif = re.compile(
        r"^\s*(?P<ifname>\S+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
        r"(?P<mask>\d+\.\d+\.\d+\.\d+)\s*(?P<vid>\d+|\-)?\s*",
        re.MULTILINE,
    )
    rx_ipif_vlan = re.compile(r"^\s*host join vlan: (?P<vid>\d+)\s*\n", re.MULTILINE)
    rx_vlan1 = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s.+\n(^.+\n)?^\s+enabled\s+.+\n"
        r"^\s*(?P<ports>\S+) (?P<eports>\S+)\s*\n"
        r"^\s*(?P<mode>\S+) (?P<emode>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_vlan2 = re.compile(r"^\s*(?P<port>\S*\d+)\s+(?P<pvid>\d+)\s+.+\n", re.MULTILINE)
    rx_mac = re.compile(r"^\s*mac address\s*: (?P<mac>\S+)\s*\n", re.MULTILINE | re.IGNORECASE)

    def execute(self):
        interfaces = []
        iface_mac = []
        vlans = []
        for match in self.rx_vlan1.finditer(self.cli("switch vlan show *")):
            vlans += [
                {
                    "vid": int(match.group("vlan_id")),
                    "ports": "%s%s" % (match.group("ports"), match.group("eports")),
                    "mode": "%s%s" % (match.group("mode"), match.group("emode")),
                }
            ]
        port_num = 0
        for match in self.rx_vlan2.finditer(self.cli("switch vlan portshow")):
            untagged = 0
            tagged = []
            ifname = self.profile.convert_interface_name(match.group("port"))
            for v in vlans:
                if v["ports"][port_num] == "F" and v["mode"][port_num] == "U":
                    untagged = v["vid"]
                if v["ports"][port_num] == "F" and v["mode"][port_num] == "T":
                    tagged += [v["vid"]]
            iface = {"name": ifname, "type": "physical", "subinterfaces": []}
            if ifname.startswith("Enet"):
                iface["subinterfaces"] += [{"name": ifname, "enabled_afi": ["BRIDGE"]}]
                if untagged:
                    iface["subinterfaces"][0]["untagged_vlan"] = untagged
                if tagged:
                    iface["subinterfaces"][0]["tagged_vlans"] = tagged
            interfaces += [iface]
            port_num += 1
        try:
            pvc_show = self.cli("adsl pvc show")
        except:
            pvc_show = self.cli("vdsl pvc show")
        for match in self.rx_sub_pvc.finditer(pvc_show):
            ifname = match.group("sub")
            for i in interfaces:
                if ifname == i["name"]:
                    sub = {
                        "name": ifname,
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "vpi": int(match.group("vpi")),
                        "vci": int(match.group("vci")),
                    }
                    if match.group("pvid") != "*":
                        sub["vlan_ids"] = int(match.group("pvid"))
                    i["subinterfaces"] += [sub]
        match = self.rx_mac.search(self.cli("sys info show"))
        iface_mac += [{"ifname": "Ethernet", "mac": match.group("mac")}]
        c = self.cli("ip show")
        for match in self.rx_ipif.finditer(c):
            ifname = match.group("ifname")
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            iface = {
                "name": ifname,
                "type": "SVI",
                "admin_status": True,  # always True, since inactive
                "oper_status": True,  # SVIs aren't shown at all
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": True,
                        "oper_status": True,
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [ip_address],
                    }
                ],
            }
            if (match.group("vid") is not None) and (match.group("vid") != "-"):
                iface["subinterfaces"][0]["vlan_ids"] = [int(match.group("vid"))]
            elif match.group("vid") is None:
                match = self.rx_ipif_vlan.search(self.cli("switch vlan cpu show"))
                iface["subinterfaces"][0]["vlan_ids"] = [int(match.group("vid"))]
            for m in iface_mac:
                if ifname == m["ifname"]:
                    iface["mac"] = m["mac"]
                    iface["subinterfaces"][0]["mac"] = m["mac"]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
