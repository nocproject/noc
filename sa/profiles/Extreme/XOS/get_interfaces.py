# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4
##
## @todo: IPv6 Support, only SNMP version, vrf support
##


class Script(NOCScript):
    """
    Extreme.XOS.get_interfaces
    """
    name = "Extreme.XOS.get_interfaces"
    implements = [IGetInterfaces]

    rx_ifidx_phys = re.compile("^X\S+\s+Port\s+(?P<port>\d+)", re.IGNORECASE)
    rx_ifidx_vlan = re.compile(
        "^VLAN\s+\S+\s+\((?P<port>\S+)\)", re.IGNORECASE)

    rx_status = re.compile(
        r"^(?P<interface>\d+)\s+(\S+)?(\s+\S+)?(\s+)?(?P<admin_status>\S)\s+"
        r"(?P<oper_status>\S)(\s+\S+)?(\s+\S+)?$",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)
    rx_sh_ipcfg = re.compile(
        r"^(?P<interface>\S+)\s+(?P<ipaddr>\S+)\s+(?P<ipmask>\S+)\s+"
        r"(?P<ifflags>\S+)\s+(?P<numseconary>\d)",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)
    rx_status_tag = re.compile(
        r"^Admin\s+State:\s+(?P<admin_status>\S+)\s+Tagging:(\s+)?"
        r"(?P<tagmode>.+?)$", re.IGNORECASE | re.DOTALL)
    rx_tag = re.compile(r"^802.1Q\s+Tag\s+(?P<tag>\d+)\s*$", re.IGNORECASE)
    rx_tagloop = re.compile(
        r"^Untagged\s+\(Internal\s+tag\s+(?P<tag>\d+)\)*$", re.IGNORECASE)
    rx_svidescr = re.compile(
        r"^Description:\s+(?P<description>.+?)$", re.IGNORECASE)
    rx_ip = re.compile(
        r"^Primary\s+IP(\s+)?:\s+(?P<address>\S+)$",
        re.IGNORECASE | re.MULTILINE)
    rx_sec_ip = re.compile(
        r"^Secondary\s+IPs(\s+)?:\s+(?P<address>.+?)$",
        re.IGNORECASE | re.MULTILINE)

    def execute(self):
        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        portchannel_members = {}  # member -> (portchannel, type)
        portchan_masters = {}
        with self.cached():
            portchannels = self.scripts.get_portchannel()
            for pc in portchannels:
                i = pc["interface"]
                t = pc["type"] == "L"
                portchan_masters[i] = i
                for m in pc["members"]:
                    portchannel_members[m] = (i, t)
        # get IfIndex
        ifidxs = {}
        try:
            for oid, vv in self.snmp.getnext("1.3.6.1.2.1.2.2.1.2"):
                vv = self.profile.convert_interface_name(vv)
                match = self.rx_ifidx_phys.match(vv)
                if match:
                    vv = match.group("port")
                    ifidxs[vv] = int(oid.split(".")[-1])
                match = self.rx_ifidx_vlan.match(vv)
                if match:
                    vv = match.group("port")
                    ifidxs[vv] = int(oid.split(".")[-1])
        except self.snmp.TimeOutError:
            ifidxs = {}
        # Get port-to-vlan mappings
        pvm = {}
        switchports = {}  # interface -> (untagged, tagged)
        for swp in self.scripts.get_switchport():
            switchports[swp["interface"]] = (
                    swp["untagged"] if "untagged" in swp else None,
                    swp["tagged"],
                    swp["description"],
                    swp["status"]
                    )

        interfaces = []
        aggrifaces = []
        # Get L3 interfaces
        ip_int = self.cli("show ipconfig")  # Get L3 VLANS
        for match in self.rx_sh_ipcfg.finditer(ip_int):
            enabled_afi = []
            sviintrf = match.group("interface")
            svicfg = self.cli("show vlan %s" % sviintrf)
            ip_list = []
            description = ""
            for sv in svicfg.strip().split("\n"):
                mt = self.rx_svidescr.search(sv.strip())  # get SVI description
                if mt:
                    description = mt.group("description")
                # SVI vlan TAG & admin mode
                mt = self.rx_status_tag.search(sv.strip())
                if mt:
                    a_stat = mt.group("admin_status").lower() == "enabled"
                    # TAG search
                    tagmode = mt.group("tagmode").strip()
                    tg = self.rx_tag.search(tagmode)
                    if tg:
                        vltag = tg.group("tag")
                    else:
                        # loopback TAG search
                        tg = self.rx_tagloop.search(tagmode)
                        vltag = tg.group("tag")
                mt = self.rx_ip.search(sv.strip())  # Primary IP
                if mt:
                    ip_list += [mt.group("address")]
                    ip_interfaces = "ipv4_addresses"
                    enabled_afi += ["IPv4"]
                mt = self.rx_sec_ip.search(sv.strip())  # Secondary IP's
                if mt:
                    sec_ip = mt.group("address")
                    for s_ip in sec_ip.split(","):
                        s_ip = s_ip.strip()
                        ip_list += [s_ip]
            iface = {
                "name": sviintrf,
                "type": "SVI",
                "admin_status": a_stat,
                "oper_status": a_stat,
                "mac": mac,
                "description": description,
                "subinterfaces": [{
                        "name": sviintrf,
                        "description": description,
                        "admin_status": a_stat,
                        "oper_status": a_stat,
                        "enabled_afi": enabled_afi,
                        ip_interfaces: ip_list,
                        "mac": mac,
                        "vlan_ids": self.expand_rangelist(vltag),
                        }]
            }
            interfaces += [iface]
        # Get L2 interfaces
        status = self.cli("sh ports no-refresh")
        for ss in status.split("\n"):
            match = self.rx_status.match(ss.strip())
            if match:
                ifname = match.group("interface")
                a_stat = match.group("admin_status").upper() == "E"
                o_stat = match.group("oper_status").upper() == "A"
                ifnaggr = "T%s" % ifname
                if ifnaggr in portchan_masters:  # Portchannel interface
                    iftype = "aggregated"
                    aggriface = {
                        "name": ifnaggr,
                        "type": iftype,
                        "admin_status": switchports[ifname][3],
                        "oper_status": o_stat,
                        "mac": mac,
                        "description": switchports[ifname][2],
                        "snmp_ifindex": (ifidxs[ifname] if ifidxs else None),
                        "subinterfaces": [{
                            "name": ifnaggr,
                            "description": switchports[ifname][2],
                            "admin_status": switchports[ifname][3],
                            "oper_status": o_stat,
                            "enabled_afi": ["BRIDGE"],
                            "mac": mac,
                            "snmp_ifindex": (
                                ifidxs[ifname] if ifidxs else None
                            )
                        }]
                    }
                if switchports[ifname][1]:
                    aggriface["subinterfaces"][0]["tagged_vlans"] = \
                        switchports[ifname][1]
                else:
                    iface["subinterfaces"][0]["tagged_vlans"] = []
                if switchports[ifname][0]:
                    aggriface["subinterfaces"][0]["untagged_vlan"] = \
                        switchports[ifname][0]
                else:
                    iface["subinterfaces"][0]["untagged_vlan"] = ""
                aggriface["description"] = switchports[ifname][2]
                aggrifaces += [aggriface]
            else:
                iftype = "physical"
                iface = {
                    "name": ifname,
                    "type": iftype,
                    "admin_status": switchports[ifname][3],
                    "oper_status": o_stat,
                    "mac": mac,
                    "description": switchports[ifname][2],
                    "snmp_ifindex": (ifidxs[ifname] if ifidxs else None),
                    "subinterfaces": [{
                        "name": ifname,
                        "description": switchports[ifname][2],
                        "admin_status": switchports[ifname][3],
                        "oper_status": o_stat,
                        "enabled_afi": ["BRIDGE"],
                        "mac": mac,
                        "snmp_ifindex": (ifidxs[ifname] if ifidxs else None)
                    }]
                }

            if switchports[ifname][1]:
                iface["subinterfaces"][0]["tagged_vlans"] = \
                    switchports[ifname][1]
            else:
                iface["subinterfaces"][0]["tagged_vlans"] = []
            if switchports[ifname][0]:
                iface["subinterfaces"][0]["untagged_vlan"] = \
                    switchports[ifname][0]
            else:
                iface["subinterfaces"][0]["untagged_vlan"] = ""
            iface["description"] = switchports[ifname][2]

            # Portchannel member
            if ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                iface["aggregated_interface"] = ai
                if is_lacp:
                    iface["enabled_protocols"] = ["LACP"]

            interfaces += [iface]
        interfaces += aggrifaces
        return [{"interfaces": interfaces}]
