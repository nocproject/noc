# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2800.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    """
    @todo: STP, CTP, GVRP, LLDP, UDLD
    @todo: IGMP
    @todo: IPv6
    """
    name = "Qtech.QSW2800.get_interfaces"
    interface = IGetInterfaces

    rx_interface = re.compile(
        r"^\s*(?P<interface>\S+) is (?P<admin_status>\S*\s*\S+), "
        r"line protocol is (?P<oper_status>\S+)"
    )
    rx_description = re.compile(
        r"alias name is (?P<description>[A-Za-z0-9\-_/\.\s\(\)]*)"
    )
    rx_ifindex = re.compile(r"index is (?P<ifindex>\d+)$")
    rx_ipv4 = re.compile(r"^\s+(?P<ip>[\d+\.]+)\s+(?P<mask>[\d+\.]+)\s+")
    rx_mac = re.compile(r"address is (?P<mac>[0-9a-f\-]+)$", re.IGNORECASE)
    rx_mtu = re.compile(r"^\s+MTU(?: is)? (?P<mtu>\d+) bytes")
    rx_oam = re.compile(r"Doesn\'t (support efmoam|enable EFMOAM!)")
    rx_vid = re.compile(r"(?P<vid>\d+)")
    MAX_REPETITIONS = 10
    MAX_GETNEXT_RETIRES = 1

    def get_lldp(self):
        v = self.cli("show lldp")
        r = []
        for l in v.splitlines():
            if "LLDP enabled port" in l:
                r = l.split(":")[1].split()
        return r

    def execute_cli(self):
        # get interfaces' status
        int_status = {}
        for s in self.scripts.get_interface_status():
            int_status[s["interface"]] = s["oper_status"]

        # get switchports
        swports = {}
        for sp in self.scripts.get_switchport():
            swports[sp["interface"]] = (
                sp["untagged"] if "untagged" in sp else None,
                sp["tagged"]
            )

        # get portchannels
        pc_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                pc_members[m] = (i, t)

        # Get LLDP port
        lldp = self.get_lldp()
        # process all interfaces and form result
        r = []
        cmd = self.cli("show interface")
        for l in cmd.splitlines():
            # find interface name
            match = self.rx_interface.match(l)
            if match:
                ifname = match.group("interface")
                # some initial settings
                iface = {
                    "name": ifname,
                    "admin_status": True,
                    "enabled_protocols": [],
                    "subinterfaces": []
                }
                # detect interface type
                if ifname.startswith("Eth"):
                    iface["type"] = "physical"
                elif ifname.startswith("Po") or ifname.startswith("Vsf"):
                    iface["type"] = "aggregated"
                elif ifname.startswith("Vlan"):
                    iface["type"] = "SVI"
                # get interface statuses
                iface["oper_status"] = int_status.get(ifname, False)
                if match.group("admin_status").startswith("administratively"):
                    iface["admin_status"] = False
                # proccess LLDP
                if ifname in lldp:
                    iface["enabled_protocols"] += ["LLDP"]
                # process portchannels' members
                if ifname in pc_members:
                    iface["aggregated_interface"] = pc_members[ifname][0]
                    if pc_members[ifname][1]:
                        iface["enabled_protocols"] += ["LACP"]
                try:
                    if ifname.startswith("Ethernet"):
                        v = self.cli("show ethernet-oam local interface %s" % ifname)
                        match = self.rx_oam.search(v)
                        if not match:
                            iface["enabled_protocols"] += ["OAM"]
                except self.CLISyntaxError:
                    pass
                # process subinterfaces
                if "aggregated_interface" not in iface:
                    sub = {
                        "name": ifname,
                        "admin_status": iface["admin_status"],
                        "oper_status": iface["oper_status"],
                        "enabled_afi": []
                    }
                    # process switchports
                    if ifname in swports:
                        u, t = swports[ifname]
                        if u:
                            sub["untagged_vlan"] = u
                        if t:
                            sub["tagged_vlans"] = t
                        sub["enabled_afi"] += ["BRIDGE"]
                else:
                    sub = {}
            # get snmp ifindex
            match = self.rx_ifindex.search(l)
            if match:
                sub["snmp_ifindex"] = match.group("ifindex")
                iface["snmp_ifindex"] = match.group("ifindex")
            # get description
            match = self.rx_description.search(l)
            if match:
                descr = match.group("description")
                if "(null)" not in descr:
                    iface["description"] = descr
                    sub["description"] = descr
            # get ipv4 addresses
            match = self.rx_ipv4.match(l)
            if match:
                if "ipv4 addresses" not in sub:
                    sub["enabled_afi"] += ["IPv4"]
                    sub["ipv4_addresses"] = []
                    vid = self.rx_vid.search(ifname)
                    sub["vlan_ids"] = [int(vid.group("vid"))]
                ip = IPv4(
                    match.group("ip"), netmask=match.group("mask")
                ).prefix
                sub["ipv4_addresses"] += [ip]
            # get mac address
            match = self.rx_mac.search(l)
            if match:
                iface["mac"] = match.group("mac")
                sub["mac"] = iface["mac"]
            # get mtu address
            match = self.rx_mtu.search(l)
            if match:
                sub["mtu"] = match.group("mtu")
                if iface.get("aggregated_interface"):
                    iface["subinterfaces"] = []
                else:
                    iface["subinterfaces"] += [sub]
                r += [iface]
        return [{"interfaces": r}]
