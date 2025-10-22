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
from noc.core.mac import MAC


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
    rx_switchport = re.compile(
        r"(?P<interface>\S+\d+(/\d+)?)\n"
        r"Type :(?P<type>Universal|"
        r"Aggregation(?: member)?)\n"
        r"(?:Mac addr num: No limit\n)?"
        r"Mode :\S+\s*\nPort VID :(?P<pvid>\d+)\n"
        r"((?:Hybrid tag|Trunk) allowed Vlan:"
        r"\s+(?P<tags>\S+))?",
        re.MULTILINE,
    )
    rx_description = re.compile(r"alias name is (?P<description>[A-Za-z0-9\-_/\.\s\(\)]*)")
    rx_ifindex = re.compile(r"index is (?P<ifindex>\d+)$")
    rx_ipv4 = re.compile(r"^\s+(?P<ip>[\d+\.]+)\s+(?P<mask>[\d+\.]+)\s+")
    rx_mac = re.compile(r"address is (?P<mac>[0-9a-f\-]+)$", re.IGNORECASE)
    rx_mtu = re.compile(r"^\s+MTU(?: is)? (?P<mtu>\d+) bytes")
    rx_oam = re.compile(r"Doesn\'t (support efmoam|enable EFMOAM!)")
    rx_vid = re.compile(r"(?P<vid>\d+)")
    rx_interface_lag = re.compile(
        r"^\s+(?P<interface>\S+) is LAG member port, LAG port:(?P<pc>\S+)", re.MULTILINE
    )
    MAX_REPETITIONS = 10
    MAX_GETNEXT_RETIRES = 1

    def get_lldp(self):
        v = self.cli("show lldp")
        r = []
        for l in v.splitlines():
            if "LLDP enabled port" in l:
                r = l.split(":")[1].split()
        return r

    def get_interface_oam(self, ifname):
        try:
            v = self.cli("show ethernet-oam local interface %s" % ifname)
            match = self.rx_oam.search(v)
            if not match:
                return True
        except self.CLISyntaxError:
            pass

    def get_port_vlans(self):
        r = {}
        # @todo 'show vlan' parser
        # @todo add QinQ translation parser
        v = self.cli("show switchport interface")
        for match in self.rx_switchport.finditer(v):
            ifname = match.group("interface")
            pvid = int(match.group("pvid"))
            # initial data
            r[ifname] = {
                "interface": ifname,
                "tagged": [],
                "untagged": pvid,
                "802.1ad Tunnel": False,
            }
            if match.group("tags"):
                ma_group = match.group("tags").replace(";", ",")
                if "showOneSwitchPort" in ma_group:
                    continue
                for tag in self.expand_rangelist(ma_group):
                    if tag != pvid:
                        r[ifname]["tagged"] += [tag]
        return r

    def execute_cli(self):
        # get switchports
        swports = self.get_port_vlans()

        # Get LLDP port
        lldp = self.get_lldp()
        # process all interfaces and form result
        r = []
        cmd = self.cli("show interface", cached=True)
        for l in cmd.splitlines():
            # find interface name
            match = self.rx_interface.match(l)
            if match:
                ifname = match.group("interface")
                # some initial settings
                iface = {
                    "name": ifname,
                    "admin_status": "up" in match.group("admin_status"),
                    "oper_status": "up" in match.group("oper_status"),
                    "enabled_protocols": [],
                    "subinterfaces": [],
                }
                iftype = self.profile.get_interface_type(ifname)
                iface["type"] = iftype
                # proccess LLDP
                if ifname in lldp:
                    iface["enabled_protocols"] += ["LLDP"]
                if ifname.startswith("Ethernet"):
                    if self.get_interface_oam(ifname):
                        iface["enabled_protocols"] += ["OAM"]
                # process subinterfaces
                if "aggregated_interface" not in iface:
                    sub = {
                        "name": ifname,
                        "admin_status": iface["admin_status"],
                        "oper_status": iface["oper_status"],
                        "enabled_afi": [],
                    }
                    # process switchports
                    if ifname in swports:
                        u, t = swports[ifname]["untagged"], swports[ifname]["tagged"]
                        if u:
                            sub["untagged_vlan"] = u
                        if t:
                            sub["tagged_vlans"] = t
                        sub["enabled_afi"] += ["BRIDGE"]
                else:
                    sub = {}
            match = self.rx_interface_lag.search(l)
            if match:
                iface["aggregated_interface"] = self.profile.convert_interface_name(
                    match.group("pc")
                )
                iface["enabled_protocols"] += ["LACP"]
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
                ip = IPv4(match.group("ip"), netmask=match.group("mask")).prefix
                sub["ipv4_addresses"] += [ip]
            # management interface may have IP address
            if l.strip() == "IPv4 address is:" and iface["name"] == "Ethernet0":
                iface["type"] = "management"
            # get mac address
            match = self.rx_mac.search(l)
            if match and MAC(match.group("mac")) != "00:00:00:00:00:00":
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
            # the following lines are not important
            if l.strip() == "Input packets statistics:":
                r += [iface]
        return [{"interfaces": r}]
