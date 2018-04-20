# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Qtech.QSW2800.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Qtech.QSW2800.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

# Python modules
import re
# NOC modules
<<<<<<< HEAD
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
=======
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(NOCScript):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    @todo: STP, CTP, GVRP, LLDP, UDLD
    @todo: IGMP
    @todo: IPv6
    """
    name = "Qtech.QSW2800.get_interfaces"
<<<<<<< HEAD
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
=======
    implements = [IGetInterfaces]

    rx_interface = re.compile(r"^\s*(?P<interface>\S+) is "
                    r"(?P<admin_status>\S*\s*\S+), "
                    r"line protocol is (?P<oper_status>\S+)")
    rx_description = re.compile(r"alias name is "
                    r"(?P<description>[A-Za-z0-9\-_/\.\s\(\)]*)")
    rx_ifindex = re.compile(r"index is (?P<ifindex>\d+)$")
    rx_ipv4 = re.compile(r"^\s+(?P<ip>[\d+\.]+)\s+(?P<mask>[\d+\.]+)\s+")
    rx_mac = re.compile(r"address is (?P<mac>[0-9a-f\-]+)$", re.IGNORECASE)

    def execute(self):
        # get interfaces' status
        int_status = {}
        for s in self.scripts.get_interface_status():
            int_status[s["interface"]] = s["status"]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

        # get switchports
        swports = {}
        for sp in self.scripts.get_switchport():
<<<<<<< HEAD
            swports[sp["interface"]] = (
                sp["untagged"] if "untagged" in sp else None,
                sp["tagged"]
            )
=======
            swports[sp["interface"]] = (sp["untagged"] if "untagged" in sp
                                                    else None, sp["tagged"])
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

        # get portchannels
        pc_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
<<<<<<< HEAD
                pc_members[m] = (i, t)

        # Get LLDP port
        lldp = self.get_lldp()
=======
                pc_members[m] = (i,t)

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
                elif ifname.startswith("Po") or ifname.startswith("Vsf"):
=======
                elif ifname.startswith("Po"):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    iface["type"] = "aggregated"
                elif ifname.startswith("Vlan"):
                    iface["type"] = "SVI"
                # get interface statuses
                iface["oper_status"] = int_status.get(ifname, False)
                if match.group("admin_status").startswith("administratively"):
                    iface["admin_status"] = False
<<<<<<< HEAD
                # proccess LLDP
                if ifname in lldp:
                    iface["enabled_protocols"] += ["LLDP"]
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                # process portchannels' members
                if ifname in pc_members:
                    iface["aggregated_interface"] = pc_members[ifname][0]
                    if pc_members[ifname][1]:
                        iface["enabled_protocols"] += ["LACP"]
<<<<<<< HEAD
                try:
                    if ifname.startswith("Ethernet"):
                        v = self.cli("show ethernet-oam local interface %s" % ifname)
                        match = self.rx_oam.search(v)
                        if not match:
                            iface["enabled_protocols"] += ["OAM"]
                except self.CLISyntaxError:
                    pass
=======
                        iface["is_lacp"] = True # @todo: Deprecated
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
                        u, t = swports[ifname]
=======
                        u,t = swports[ifname]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                        if u:
                            sub["untagged_vlan"] = u
                        if t:
                            sub["tagged_vlans"] = t
                        sub["enabled_afi"] += ["BRIDGE"]
<<<<<<< HEAD
                else:
                    sub = {}
=======
                        sub["is_bridge"] = True # @todo: Deprecated
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            # get snmp ifindex
            match = self.rx_ifindex.search(l)
            if match:
                sub["snmp_ifindex"] = match.group("ifindex")
<<<<<<< HEAD
                iface["snmp_ifindex"] = match.group("ifindex")
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            # get description
            match = self.rx_description.search(l)
            if match:
                descr = match.group("description")
<<<<<<< HEAD
                if "(null)" not in descr:
=======
                if not "(null)" in descr:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    iface["description"] = descr
                    sub["description"] = descr
            # get ipv4 addresses
            match = self.rx_ipv4.match(l)
            if match:
<<<<<<< HEAD
                if "ipv4 addresses" not in sub:
                    sub["enabled_afi"] += ["IPv4"]
                    sub["ipv4_addresses"] = []
                    vid = self.rx_vid.search(ifname)
                    sub["vlan_ids"] = [int(vid.group("vid"))]
                ip = IPv4(
                    match.group("ip"), netmask=match.group("mask")
                ).prefix
=======
                if not "ipv4 addresses" in sub:
                    sub["enabled_afi"] += ["IPv4"]
                    sub["is_ipv4"] = True # @todo: Deprecated
                    sub["ipv4_addresses"] = []
                    vid = re.search("(?P<vid>\d+)", ifname)
                    sub["vlan_ids"] = [int(vid.group("vid"))]
                ip = IPv4(match.group("ip"),
                            netmask=match.group("mask")).prefix
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                sub["ipv4_addresses"] += [ip]
            # get mac address
            match = self.rx_mac.search(l)
            if match:
                iface["mac"] = match.group("mac")
                sub["mac"] = iface["mac"]
<<<<<<< HEAD
            # get mtu address
            match = self.rx_mtu.search(l)
            if match:
                sub["mtu"] = match.group("mtu")
                if iface.get("aggregated_interface"):
                    iface["subinterfaces"] = []
                else:
                    iface["subinterfaces"] += [sub]
                r += [iface]
=======
                iface["subinterfaces"] += [sub]
                r += [iface]

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return [{"interfaces": r}]
