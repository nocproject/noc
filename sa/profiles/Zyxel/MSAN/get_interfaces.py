# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.MSAN.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Zyxel.MSAN.get_interfaces"
    interface = IGetInterfaces

    rx_enet = re.compile(
        r"^\s*(?P<ifname>(enet|sub|up)\d+)\s+(?P<descr>.*)\s+"
        r"(?P<admin_status>V|\-)\s+ (?:sub|up)\s+.+$", re.MULTILINE)
    rx_enet_o = re.compile(
        r"^\s*(switch )?port (?:enet|sub|up)\d+:\n\s*link status: (?P<oper_status>\S+|down)",
        re.MULTILINE)
    rx_sub_pvc1 = re.compile(
        r"^\s*(?P<sub>\d+\-\d+)-(?P<vpi>\d+)/(?P<vci>\d+)\s+\S+\s+\S+\s+"
        r"(?P<pvid>\d+)\s+", re.MULTILINE)
    rx_sub_pvc2 = re.compile(
        r"^\s*(?P<sub>\d+)\s+(?P<vpi>\d+)\s+(?P<vci>\d+)\s+(?P<pvid>\S+)\s+",
        re.MULTILINE)
    rx_sub_o = re.compile(
        r"^\s*(?P<sub>\d+\s*\-\s*\d+)\s+(?P<admin_status>V|\-)",
        re.MULTILINE)
    rx_sub_o2 = re.compile(
        r"^\s*Port (?P<sub>\d+): (?P<admin_status>Up|Down)",
        re.MULTILINE)
    rx_ipif = re.compile(
        r"^\s*(?P<ifname>\S+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
        r"(?P<mask>\d+\.\d+\.\d+\.\d+)\s*(?P<vid>\d+|\-)?\s*$", re.MULTILINE)
    rx_ipif1 = re.compile(
        r"^\s*device\s+(?P<ifname>\S+)\s+\S+\s+\S+\s+mtu\s+(?P<mtu>\d+)\s+"
        r"(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mask>\d+\.\d+\.\d+\.\d+)\s*$",
        re.MULTILINE)
    rx_ipif_mac = re.compile(
        r"^\s*(?P<ifname>\S+) mac\s+: (?P<mac>\S+)\s*\n", re.MULTILINE)
    rx_ipif_vlan = re.compile(
        r"^\s*host join vlan: (?P<vid>\d+)\s*\n", re.MULTILINE)
    rx_vlan1 = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<ports>\S+)/(?P<mode>\S+)\s+\S+\s*"
        r"(?P<name>.*)$", re.MULTILINE)
    rx_vlan2 = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s.+\n(^.+\n)?^\s+enabled\s+.+\n"
        r"^\s*(?P<ports>\S+) (?P<eports>\S+)\s*\n"
        r"^\s*(?P<mode>\S+) (?P<emode>\S+)\s*\n", re.MULTILINE)
    rx_vlan3 = re.compile(
        r"^\s*(?P<port>\S*\d+)\s+(?P<pvid>\d+)\s+.+\n", re.MULTILINE)
    rx_vlan4 = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+\-\s+(?P<tagged>v)\s+.+\n", re.MULTILINE)
    rx_vlan5 = re.compile(
        r"^\s*Port\s+0:\s+(?P<vlan_id>\d+)\s*\n", re.MULTILINE)
    rx_mac = re.compile(
        r"^\s*mac address\s*: (?P<mac>\S+)\s*\n", re.MULTILINE | re.IGNORECASE)
    rx_ports = re.compile(
        r"^Port\s+\d+\s+\((?P<port>ethernet|adsl\d+)\): (?:Enabled|Disabled)\s*\n",
        re.MULTILINE)
    rx_stp = re.compile(r"^\s*(?P<port>\S+)\s+V\s+\d+\s+", re.MULTILINE)

    def get_stp(self):
        try:
            v = self.cli("switch port mstp show 0")
        except self.CLISyntaxError:
            return []
        r = []
        for match in self.rx_stp.finditer(v):
            r += [match.group("port")]
        return r

    def execute(self):
        slots = self.profile.get_slots_n(self)
        interfaces = []
        iface_mac = []
        vlans = []
        stps = self.get_stp()
        if slots > 1:
            for match in self.rx_vlan1.finditer(self.cli("vlan show")):
                vlans += [{
                    "vid": int(match.group("vlan_id")),
                    "ports": match.group("ports"),
                    "mode": match.group("mode")
                }]
            port_num = 0
            for match in self.rx_enet.finditer(self.cli("switch port show")):
                untagged = 0
                tagged = []
                admin_status = match.group("admin_status") == "V"
                ifname = self.profile.convert_interface_name(match.group("ifname"))
                match1 = self.rx_enet_o.search(self.cli("show enet %s" % ifname))
                if match1:
                    oper_status = match1.group("oper_status") != "down"
                else:
                    raise self.NotSupportedError()
                for v in vlans:
                    if v["ports"][port_num] == "F" \
                    and v["mode"][port_num] == "U":
                        untagged = v["vid"]
                    if v["ports"][port_num] == "F" \
                    and v["mode"][port_num] == "T":
                        tagged += [v["vid"]]
                iface = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "enabled_protocols": [],
                    "subinterfaces": [{
                        "name": ifname,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["BRIDGE"]
                    }]
                }
                if untagged:
                    iface["subinterfaces"][0]["untagged_vlan"] = untagged
                if tagged:
                    iface["subinterfaces"][0]["tagged_vlans"] = tagged
                if ifname in stps:
                    iface["enabled_protocols"] += ["STP"]
                interfaces += [iface]
                port_num += 1
            for i in range(1, slots):
                v = self.cli("port show %s" % i)
                for match in self.rx_sub_o.finditer(v):
                    admin_status = match.group("admin_status") == "V"
                    iface = {
                        "name": match.group("sub").replace(" ", ""),
                        "admin_status": admin_status,
                        "type": "physical",
                        "subinterfaces": []
                    }
                    interfaces += [iface]
                v = self.cli("port show %s pvc" % i)
                for match in self.rx_sub_pvc1.finditer(v):
                    ifname = match.group("sub")
                    for iface in interfaces:
                        if iface["name"] == ifname:
                            iface["subinterfaces"] += [{
                                "name": "%s.%s" % (ifname, match.group("pvid")),
                                "admin_status": iface["admin_status"],
                                "enabled_afi": ["BRIDGE", "ATM"],
                                "vlan_ids": int(match.group("pvid")),
                                "vpi": int(match.group("vpi")),
                                "vci": int(match.group("vci"))
                            }]
                            break
                v = self.cli("lcman show %s" % i)
                for match in self.rx_ipif_mac.finditer(v):
                    iface_mac += [match.groupdict()]
        else:
            ver = self.scripts.get_version()
            if ver["platform"] in ["IES-1248", "IES-612"]:
                for match in self.rx_vlan2.finditer(self.cli("switch vlan show *")):
                    vlans += [{
                        "vid": int(match.group("vlan_id")),
                        "ports": "%s%s" % (match.group("ports"), match.group("eports")),
                        "mode": "%s%s" % (match.group("mode"), match.group("emode"))
                    }]
                port_num = 0
                for match in self.rx_vlan3.finditer(self.cli("switch vlan portshow")):
                    untagged = 0
                    tagged = []
                    ifname = self.profile.convert_interface_name(match.group("port"))
                    for v in vlans:
                        if v["ports"][port_num] == "F" \
                        and v["mode"][port_num] == "U":
                            untagged = v["vid"]
                        if v["ports"][port_num] == "F" \
                        and v["mode"][port_num] == "T":
                            tagged += [v["vid"]]
                    iface = {
                        "name": ifname,
                        "type": "physical",
                        "subinterfaces": []
                    }
                    if ifname.startswith("Enet"):
                        iface["subinterfaces"] += [{
                            "name": ifname,
                            "enabled_afi": ["BRIDGE"]
                        }]
                        if untagged:
                            iface["subinterfaces"][0]["untagged_vlan"] = untagged
                        if tagged:
                            iface["subinterfaces"][0]["tagged_vlans"] = tagged
                    interfaces += [iface]
                    port_num += 1
                for match in self.rx_sub_pvc2.finditer(self.cli("adsl pvc show")):
                    ifname = match.group("sub")
                    for i in interfaces:
                        if ifname == i["name"]:
                            sub = {
                                "name": ifname,
                                "enabled_afi": ["BRIDGE", "ATM"],
                                "vpi": int(match.group("vpi")),
                                "vci": int(match.group("vci"))
                            }
                            if match.group("pvid") != "*":
                                sub["vlan_ids"] = int(match.group("pvid"))
                            i["subinterfaces"] += [sub]
                match = self.rx_mac.search(self.cli("sys info show"))
                iface_mac += [{"ifname": "Ethernet", "mac": match.group("mac")}]
            if ver["platform"] in ["IES-1000"]:
                adsl = self.cli("adsl show ports")
                for match in self.rx_ports.finditer(self.cli("bridge macfilter")):
                    ifname = match.group("port")
                    iface = {
                        "name": ifname,
                        "type": "physical",
                        "subinterfaces": []
                    }
                    if ifname.startswith("ethernet"):
                        sub = {
                                "name": ifname,
                                "admin_status": True,
                                "enabled_afi": ["BRIDGE"],
                                "tagged_vlans": []
                            }
                        v = self.cli("vlan1q vlan status")
                        for match in self.rx_vlan4.finditer(v):
                            vid = int(match.group("vlan_id"))
                            if vid == 1:
                                continue
                            sub["tagged_vlans"] += [vid]
                        iface["subinterfaces"] += [sub]
                        interfaces += [iface]
                    if ifname.startswith("adsl"):
                        for match in self.rx_sub_o2.finditer(adsl):
                            if match.group("sub") == ifname[4:]:
                                iface["admin_status"] = match.group("admin_status") == "Up"
                                break
                        v = self.cli("adsl show pvc %s" % ifname[4:])
                        for match in self.rx_sub_pvc2.finditer(v):
                            iface["subinterfaces"] += [{
                                "name": match.group("sub"),
                                "admin_status": iface["admin_status"],
                                "enabled_afi": ["BRIDGE", "ATM"],
                                "vlan_ids": int(match.group("pvid")) if match.group("pvid") != "*" else None,
                                "vpi": int(match.group("vpi")),
                                "vci": int(match.group("vci"))
                            }]
                        interfaces += [iface]
                c = self.cli("ip device list")
                for match in self.rx_ipif1.finditer(c):
                    ifname = match.group("ifname")
                    addr = match.group("ip")
                    mask = match.group("mask")
                    ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
                    iface = {
                        "name": ifname,
                        "type": "SVI",
                        "admin_status": True,  # always True, since inactive
                        "oper_status": True,   # SVIs aren't shown at all
                        "subinterfaces": [{
                            "name": ifname,
                            "admin_status": True,
                            "oper_status": True,
                            "mtu": int(match.group("mtu")),
                            "enabled_afi": ["IPv4"],
                            "ipv4_addresses": [ip_address],
                        }]
                    }
                    v = self.cli("vlan1q vlan status")
                    match1 = self.rx_vlan5.search(v)
                    vid = int(match1.group("vlan_id"))
                    iface["subinterfaces"][0]["vlan_ids"] = [vid]
                    ch_id = self.scripts.get_chassis_id()
                    mac = ch_id[0]["first_chassis_mac"]
                    iface["mac"] = mac
                    iface["subinterfaces"][0]["mac"] = mac
                    interfaces += [iface]
                return [{"interfaces": interfaces}]

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
                "oper_status": True,   # SVIs aren't shown at all
                "subinterfaces": [{
                    "name": ifname,
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [ip_address],
                }]
            }
            if (match.group("vid") is not None) and (match.group("vid") != "-"):
                iface["subinterfaces"][0]["vlan_ids"] = [int(match.group('vid'))]
            else:
                if match.group("vid") is None:
                    match = self.rx_ipif_vlan.search(self.cli("switch vlan cpu show"))
                    iface["subinterfaces"][0]["vlan_ids"] = [int(match.group('vid'))]
            for m in iface_mac:
                if ifname == m["ifname"]:
                    iface["mac"] = m["mac"]
                    iface["subinterfaces"][0]["mac"] = m["mac"]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
