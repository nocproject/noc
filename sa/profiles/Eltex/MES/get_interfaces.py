# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import re
import time
# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.text import parse_table
from noc.core.mac import MAC
from noc.core.mib import mib
from noc.core.ip import IPv4


class Script(BaseScript):
    """
    Eltex.MES.get_interfaces
    @todo: VRF support
    @todo: IPv6
    @todo: ISIS
    @todo: isis, bgp, rip
    @todo: subinterfaces
    @todo: Q-in-Q
    """

    name = "Eltex.MES.get_interfaces"
    cache = True
    interface = IGetInterfaces

    TIMEOUT = 300

    MAX_REPETITIONS = 20

    MAX_GETNEXT_RETIRES = 2

    BULK = None

    INTERFACE_NAMES = set()

    rx_sh_ip_int = re.compile(
        r"^(?P<ip>\d+\S+)/(?P<mask>\d+)\s+(?P<interface>.+?)\s+"
        r"((?P<admin_status>UP|DOWN)/(?P<oper_status>UP|DOWN)\s+)?"
        r"(?:Static|Dinamic|DHCP)\s", re.MULTILINE
    )
    rx_ifname = re.compile(r"^(?P<ifname>\S+)\s+\S+\s+(?:Enabled|Disabled).+$", re.MULTILINE)
    rx_sh_int = re.compile(
        r"^(?P<interface>.+?)\sis\s(?P<oper_status>up|down)\s+"
        r"\((?P<admin_status>connected|not connected|admin.shutdown|error-disabled)\)\s*\n"
        r"^\s+Interface index is (?P<ifindex>\d+)\s*\n"
        r"^\s+Hardware is\s+.+?, MAC address is (?P<mac>\S+)\s*\n"
        r"(^\s+Description:(?P<descr>.*?)\n)?"
        r"^\s+Interface MTU is (?P<mtu>\d+)\s*\n"
        r"(^\s+Link aggregation type is (?P<link_type>\S+)\s*\n)?"
        r"(^\s+No. of members in this port-channel: \d+ \(active \d+\)\s*\n)?"
        r"((?P<members>.+?))?(^\s+Active bandwith is \d+Mbps\s*\n)?", re.MULTILINE | re.DOTALL
    )
    rx_sh_int_des = rx_in = re.compile(
        r"^(?P<ifname>\S+)\s+(?P<oper_status>Up|Down)\s+"
        r"(?P<admin_status>Up|Down|Not Present)\s(?:(?P<descr>.*?)\n)?", re.MULTILINE
    )
    rx_sh_int_des2 = re.compile(r"^(?P<ifname>\S+\d+)(?P<descr>.*?)\n", re.MULTILINE)
    rx_lldp_en = re.compile(r"LLDP state: Enabled?")
    rx_lldp = re.compile(r"^(?P<ifname>\S+)\s+(?:Rx and Tx|Rx|Tx)\s+", re.MULTILINE)

    rx_gvrp_en = re.compile(r"GVRP Feature is currently Enabled on the device?")
    rx_gvrp = re.compile(r"^(?P<ifname>\S+)\s+(?:Enabled\s+)Normal\s+", re.MULTILINE)

    rx_stp_en = re.compile(r"Spanning tree enabled mode?")
    rx_stp = re.compile(
        r"(?P<ifname>\S+)\s+(?:enabled)\s+\S+\s+\d+\s+\S+\s+\S+\s+(?:Yes|No)", re.MULTILINE
    )

    rx_vlan = re.compile(
        r"(?P<vlan>\S+)\s+(?P<vdesc>\S+)\s+(?P<vtype>Tagged|Untagged)\s+", re.MULTILINE
    )

    def get_max_repetitions(self):
        return self.MAX_REPETITIONS

    def collect_ifnames(self):
        return self.INTERFACE_NAMES

    def get_getnext_retires(self):
        return self.MAX_GETNEXT_RETIRES

    # if ascii or rus text in description
    def convert_description(self, desc):
        if desc:
            return unicode(desc, "utf8", "replace").encode("utf8")
        else:
            return desc

    def get_bulk(self):
        return self.BULK

    def get_iftable(self, oid, transform=True):
        if "::" in oid:
            oid = mib[oid]
        for oid, v in self.snmp.getnext(oid, max_repetitions=self.get_max_repetitions(),
                                        max_retries=self.get_getnext_retires(), bulk=self.get_bulk()):
            yield int(oid.rsplit(".", 1)[-1]) if transform else oid, v

    def apply_table(self, r, mib, name, f=None):
        if not f:

            def f(x):
                return x

        for ifindex, v in self.get_iftable(mib):
            s = r.get(ifindex)
            if s:
                s[name] = f(v)

    def get_ip_ifaces(self):
        ip_iface = dict(
            (l, ".".join(o.rsplit(".")[-4:]))
            for o, l in self.get_iftable(mib["RFC1213-MIB::ipAdEntIfIndex"], False)
        )
        ip_mask = dict(
            (".".join(o.rsplit(".")[-4:]), l)
            for o, l in self.get_iftable(mib["RFC1213-MIB::ipAdEntNetMask"], False)
        )
        r = {}
        for ip in ip_iface:
            r[ip] = (ip_iface[ip], ip_mask[ip_iface[ip]])
        return r

    def get_aggregated_ifaces(self):
        portchannel_members = {}
        aggregated = []
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            aggregated += [i]
            t = pc["type"] in ["L", "LACP"]
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        return aggregated, portchannel_members

    def execute_snmp(self, interface=None):
        swports = {}
        index = self.scripts.get_ifindexes()
        aggregated, portchannel_members = self.get_aggregated_ifaces()
        ifaces = dict((index[i], {"interface": i}) for i in index)
        # Apply ifAdminStatus
        self.apply_table(ifaces, "IF-MIB::ifAdminStatus", "admin_status", lambda x: x == 1)
        # Apply ifOperStatus
        self.apply_table(ifaces, "IF-MIB::ifOperStatus", "oper_status", lambda x: x == 1)
        # Apply PhysAddress
        self.apply_table(ifaces, "IF-MIB::ifPhysAddress", "mac_address")
        self.apply_table(ifaces, "IF-MIB::ifType", "type")
        self.apply_table(ifaces, "IF-MIB::ifSpeed", "speed")
        self.apply_table(ifaces, "IF-MIB::ifMtu", "mtu")
        time.sleep(10)
        self.apply_table(ifaces, "IF-MIB::ifAlias", "description")
        ip_ifaces = self.get_ip_ifaces()
        for sp in self.scripts.get_switchport():
            swports[sp["interface"]] = (
                sp["untagged"] if "untagged" in sp else None,
                sp["tagged"]
            )
        r = []
        subs = defaultdict(list)
        """
        IF-MIB::ifPhysAddress.1 = STRING:
        IF-MIB::ifPhysAddress.2 = STRING: 0:21:5e:40:c2:50
        IF-MIB::ifPhysAddress.3 = STRING: 0:21:5e:40:c2:52
        """
        for l in ifaces:
            iface = ifaces[l]
            i_type = self.profile.get_interface_type(iface["interface"])
            if "." in iface["interface"]:
                s = {
                    "name": iface["interface"],
                    "description": self.convert_description(iface.get("description", "")),
                    "type": i_type,
                    "enabled_afi": ["BRIDGE"],
                    "admin_status": iface["admin_status"],
                    "oper_status": iface["oper_status"],
                    "snmp_ifindex": l,
                }
                iface_name, num = iface["interface"].rsplit(".", 1)
                if num.isdigit():
                    vlan_ids = int(iface["interface"].rsplit(".", 1)[-1])
                    if 1 <= vlan_ids < 4095:
                        s["vlan_ids"] = vlan_ids
                if l in ip_ifaces:
                    s["ipv4_addresses"] = [IPv4(*ip_ifaces[l])]
                    s["enabled_afi"] = ["IPv4"]
                if iface["mac_address"]:
                    s["mac"] = MAC(iface["mac_address"])
                subs[iface_name] += [s.copy()]
                # r[-1]["subinterfaces"] += [s]
                continue
            i = {
                "name": iface["interface"],
                "description": self.convert_description(iface.get("description", "")),
                "type": i_type,
                "admin_status": iface["admin_status"],
                "oper_status": iface["oper_status"],
                "snmp_ifindex": l,
            }
            if i["name"] in portchannel_members:
                i["aggregated_interface"], lacp = portchannel_members[i["name"]]
                if lacp:
                    i["enabled_protocols"] = ["LACP"]
            if i["name"] in aggregated:
                i["type"] = "aggregated"
            if iface["mac_address"]:
                i["mac"] = MAC(iface["mac_address"])
            # sub = {"subinterfaces": [i.copy()]}
            r += [i]
        for l in r:
            if l["name"] in subs:
                l["subinterfaces"] = subs[l["name"]]
            else:
                l["subinterfaces"] = [
                    {
                        "name": l["name"],
                        "description": self.convert_description(l.get("description", "")),
                        "type": "SVI",
                        "enabled_afi": ["BRIDGE"]
                        if l["type"] in ["physical", "aggregated"] else [],
                        "admin_status": l["admin_status"],
                        "oper_status": l["oper_status"],
                        "snmp_ifindex": l["snmp_ifindex"],
                    }
                ]
                if l["snmp_ifindex"] in ip_ifaces:
                    l["subinterfaces"][-1]["ipv4_addresses"] = [IPv4(*ip_ifaces[l["snmp_ifindex"]])]
                    l["subinterfaces"][-1]["enabled_afi"] = ["IPv4"]
                if swports.get(l["name"]):
                    l["subinterfaces"][0]["untagged_vlan"] = int(swports.get(l["name"])[0])
                    l["subinterfaces"][0]["tagged_vlans"] = swports.get(l["name"])[1]

        return [{"interfaces": r}]

    def execute_cli(self):
        d = {}
        if self.has_snmp():
            try:
                for s in self.snmp.getnext("1.3.6.1.2.1.2.2.1.2", max_repetitions=10):
                    n = s[1]
                    sifindex = s[0][len("1.3.6.1.2.1.2.2.1.2") + 1:]
                    if int(sifindex) < 3000:
                        sm = str(self.snmp.get("1.3.6.1.2.1.2.2.1.6.%s" % sifindex))
                        smac = MACAddressParameter().clean(sm)
                        if n.startswith("oob"):
                            continue
                        sname = self.profile.convert_interface_name(n)
                    else:
                        continue
                    d[sname] = {"sifindex": sifindex, "smac": smac}
            except self.snmp.TimeOutError:
                pass
        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)

        # Get LLDP interfaces
        lldp = []
        if self.has_capability("Network | LLDP"):
            c = self.cli("show lldp configuration", ignore_errors=True)
            if self.rx_lldp_en.search(c):
                lldp = self.rx_lldp.findall(c)

        # Get GVRP interfaces
        gvrp = []
        c = self.cli("show gvrp configuration", ignore_errors=True)
        if self.rx_gvrp_en.search(c):
            gvrp = self.rx_gvrp.findall(c)

        # Get STP interfaces
        stp = []
        if self.has_capability("Network | STP"):
            c = self.cli("show spanning-tree", ignore_errors=True)
            if self.rx_stp_en.search(c):
                stp = self.rx_stp.findall(c)

        # Get ifname and description
        c = self.cli("show interfaces description").split("\n\n")
        i = self.rx_sh_int_des.findall("".join(["%s\n\n%s" % (c[0], c[1])]))
        if not i:
            i = self.rx_sh_int_des2.findall("".join(["%s\n\n%s" % (c[0], c[1])]))

        interfaces = []
        mtu = None
        for res in i:
            mac = None
            ifindex = 0
            name = res[0].strip()
            if (self.match_version(version__regex="[12]\.[15]\.4[4-9]") or
                    self.match_version(version__regex="4\.0\.[4-7]$")):
                v = self.cli("show interface %s" % name)
                time.sleep(0.5)
                for match in self.rx_sh_int.finditer(v):
                    # ifname = match.group("interface")
                    ifindex = match.group("ifindex")
                    mac = match.group("mac")
                    mtu = match.group("mtu")
                    if len(res) == 4:
                        a_stat = res[1].strip().lower() == "up"
                        o_stat = res[2].strip().lower() == "up"
                        description = res[3].strip()
                    else:
                        a_stat = True
                        o_stat = match.group("oper_status").lower() == "up"
                        description = match.group("descr")
                        if not description:
                            description = ''

            else:
                if self.profile.convert_interface_name(name) in d:
                    ifindex = d[self.profile.convert_interface_name(name)]["sifindex"]
                    mac = d[self.profile.convert_interface_name(name)]["smac"]
                if len(res) == 4:
                    a_stat = res[1].strip().lower() == "up"
                    o_stat = res[2].strip().lower() == "up"
                    description = res[3].strip()
                else:
                    o_stat = True
                    a_stat = True
                    description = res[1].strip()

            sub = {
                "name": self.profile.convert_interface_name(name),
                "admin_status": a_stat,
                "oper_status": o_stat,
                "description": description.strip(),
                "enabled_afi": []
            }
            if mtu:
                sub["mtu"] = mtu
            if ifindex:
                sub["snmp_ifindex"] = ifindex
            if mac:
                sub["mac"] = mac
            iface = {
                "type": self.profile.get_interface_type(name),
                "name": self.profile.convert_interface_name(name),
                "admin_status": a_stat,
                "oper_status": o_stat,
                "description": description.strip(),
                "enabled_protocols": [],
                "subinterfaces": [sub]
            }
            if ifindex:
                iface["snmp_ifindex"] = ifindex
            if mac:
                iface["mac"] = mac

            # LLDP protocol
            if name in lldp:
                iface["enabled_protocols"] += ["LLDP"]
            # GVRP protocol
            if name in gvrp:
                iface["enabled_protocols"] += ["GVRP"]
            # STP protocol
            if name in stp:
                iface["enabled_protocols"] += ["STP"]
                # Portchannel member
            name = self.profile.convert_interface_name(name)
            if name in portchannel_members:
                ai, is_lacp = portchannel_members[name]
                iface["aggregated_interface"] = ai
                if is_lacp:
                    iface["enabled_protocols"] += ["LACP"]
            iface["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
            # Vlans
            cmd = self.cli("show interfaces switchport %s" % name)
            time.sleep(0.5)
            rcmd = cmd.split("\n\n")
            tvlan = []
            utvlan = None
            for vlan in parse_table(rcmd[0]):
                vlan_id = vlan[0]
                rule = vlan[2]
                if rule == "Tagged":
                    tvlan.append(int(vlan_id))
                elif rule == "Untagged":
                    utvlan = vlan_id
            iface["subinterfaces"][0]["tagged_vlans"] = tvlan
            if utvlan:
                iface["subinterfaces"][0]["untagged_vlan"] = utvlan

            cmd = self.cli("show ip interface %s" % name)
            time.sleep(0.5)
            for match in self.rx_sh_ip_int.finditer(cmd):
                if not match:
                    continue
                ip = match.group("ip")
                netmask = match.group("mask")
                ip = ip + '/' + netmask
                ip_list = [ip]
                enabled_afi = []
                if ":" in ip:
                    ip_interfaces = "ipv6_addresses"
                    enabled_afi += ["IPv6"]
                else:
                    ip_interfaces = "ipv4_addresses"
                    enabled_afi += ["IPv4"]
                iface["subinterfaces"][0]["enabled_afi"] = enabled_afi
                iface["subinterfaces"][0][ip_interfaces] = ip_list

            interfaces += [iface]

        ip_iface = self.cli("show ip interface")
        for match in self.rx_sh_ip_int.finditer(ip_iface):
            ifname = match.group("interface")
            typ = self.profile.get_interface_type(ifname)
            ip = match.group("ip")
            netmask = match.group("mask")
            ip = ip + '/' + netmask
            ip_list = [ip]
            enabled_afi = []
            if ":" in ip:
                ip_interfaces = "ipv6_addresses"
                enabled_afi += ["IPv6"]
            else:
                ip_interfaces = "ipv4_addresses"
                enabled_afi += ["IPv4"]
            if ifname.startswith("vlan"):
                vlan = ifname.split(' ')[1]
                ifname = ifname.strip()
            else:
                continue
            if match.group("admin_status"):
                a_stat = match.group("admin_status").lower() == "up"
            else:
                a_stat = True
            if match.group("oper_status"):
                o_stat = match.group("oper_status").lower() == "up"
            else:
                o_stat = True
            iface = {
                "name": self.profile.convert_interface_name(ifname),
                "type": typ,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": a_stat,
                        "oper_status": o_stat,
                        "enabled_afi": enabled_afi,
                        ip_interfaces: ip_list,
                        "vlan_ids": self.expand_rangelist(vlan),
                    }
                ]
            }
            interfaces += [iface]

        return [{"interfaces": interfaces}]
