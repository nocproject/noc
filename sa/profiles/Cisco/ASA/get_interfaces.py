# ---------------------------------------------------------------------
# Cisco.ASA.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Cisco.ASA.get_interfaces"
    interface = IGetInterfaces

    rx_int = re.compile(
        r"(?P<interface>\S+)\s\"(?P<alias>[\w-]*)\"\,\sis(\sadministratively)?"
        r"\s(?P<admin_status>up|down),\s+line\s+protocol\s+is\s+(?P<oper_status>up|down)",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_mac = re.compile(r"MAC\saddress\s(?P<mac>\w{4}\.\w{4}\.\w{4})", re.MULTILINE | re.IGNORECASE)
    rx_vlan = re.compile(r"VLAN\sIdentifier\s(?P<vlan>\w+)", re.MULTILINE | re.IGNORECASE)
    rx_ospf = re.compile(r"^(?P<name>\w+)\sis\sup|down\,", re.MULTILINE | re.IGNORECASE)
    rx_ip = re.compile(
        r"IP\saddress\s(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\, "
        r"subnet mask (?P<mask>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_snmp_int = re.compile(
        r"Interface\snumber\sis\s(?P<ifindex>\w+)", re.MULTILINE | re.IGNORECASE
    )

    def get_ospfint(self):
        v = self.cli("show ospf interface")
        ospfs = []
        for s in v.split("\n"):
            match = self.rx_ospf.search(s)
            if match:
                ospfs.append(match.group("name"))
        return ospfs

    def execute(self):
        interfaces = []
        ospfs = self.get_ospfint()
        if self.capabilities.get("Cisco | ASA | Security | Context | Mode"):
            if self.capabilities["Cisco | ASA | Security | Context | Mode"] == "multiple":
                self.cli("changeto system")
        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = self.profile.convert_interface_name(pc["interface"])
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)

        # ifindex = self.get_ifindex_map()

        v = self.cli("show interface detail")
        for s in v.split("\nInterface "):
            match = self.rx_int.search(s)
            if match:
                ifname = match.group("interface")
                if (
                    ifname.startswith("Virtual")
                    or ifname.startswith("Tunnel")
                    or ifname.startswith("Internal-")
                ):
                    continue
                a_stat = match.group("admin_status").lower() == "up"
                o_stat = match.group("oper_status").lower() == "up"
                alias = match.group("alias")
                match_mac = self.rx_mac.search(s)
                if match_mac:
                    """Hack for PortChannel sub int (it no mac in show interfaces)"""
                    mac = match_mac.group("mac")
                sub = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "description": alias,
                    "mac": mac,
                    "enabled_afi": [],
                    "enabled_protocols": [],
                }
                match = self.rx_ip.search(s)
                if match:
                    ip = IPv4(match.group("ip"), netmask=match.group("mask")).prefix
                    sub["ipv4_addresses"] = [ip]
                    sub["enabled_afi"] += ["IPv4"]
                match = self.rx_vlan.search(s)
                if match:
                    vlan = match.group("vlan")
                    if vlan != "none":
                        sub["vlan_ids"] = [vlan]
                    else:
                        self.logger.error("Not configured VlanId on subinterfaces %s" % ifname)
                match = self.rx_snmp_int.search(s)
                if match:
                    ifindex = match.group("ifindex")
                    sub["snmp_ifindex"] = ifindex

                if alias in ospfs:
                    sub["enabled_protocols"] += ["OSPF"]
                phys = ifname.find(".") == -1
                if phys:
                    iftype = self.profile.get_interface_type(ifname)
                    iface = {
                        "name": ifname,
                        "admin_status": a_stat,
                        "oper_status": o_stat,
                        "description": alias,
                        "type": iftype,
                        "mac": mac,
                        "enabled_protocols": [],
                        "subinterfaces": [sub],
                    }
                    if ifindex:
                        iface["snmp_ifindex"] = ifindex
                    # if ifname in ifindex:
                    ifname2 = self.profile.convert_interface_name(ifname)
                    # Portchannel member
                    if ifname2 in portchannel_members:
                        ai, is_lacp = portchannel_members[ifname2]
                        iface["aggregated_interface"] = ai
                        iface["enabled_protocols"] += ["LACP"]

                    interfaces += [iface]
                    if iftype == "SVI" and ifname.startswith("Vlan"):
                        vid = int(ifname[4:].strip())
                        sub["vlan_ids"] = [vid]
                elif interfaces[-1]["name"] == interfaces[-1]["subinterfaces"][-1]["name"]:
                    interfaces[-1]["subinterfaces"] = [sub]
                else:
                    interfaces[-1]["subinterfaces"] += [sub]
            else:
                continue
        return [{"interfaces": interfaces}]

    rx_int_snmp = re.compile(
        r"^Adaptive\sSecurity\sAppliance\s'(?P<interface>\S+)'\sinterface", re.IGNORECASE
    )

    def get_ifindex_map(self):
        """
        Retrieve name -> ifindex map
        """
        m = {}
        if self.has_snmp():
            try:
                # IF-MIB::ifDescr
                t = self.snmp.get_table("1.3.6.1.2.1.2.2.1.2")
                for i in t:
                    if t[i].startswith("ControlEthernet"):
                        continue
                    intf = self.rx_int_snmp.match(t[i])
                    intf.group("interface")
                    m[intf.group("interface")] = i
            except self.snmp.TimeOutError:
                pass
        return m
