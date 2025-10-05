# ---------------------------------------------------------------------
# Eltex.MES.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import time

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.text import parse_table
from noc.core.mib import mib
from noc.core.comp import smart_text, smart_bytes


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
    CHUNK_SIZE = 10
    INTERFACE_NAMES = set()

    rx_sh_ip_int = re.compile(
        r"^(?P<ip>\d+\S+)/(?P<mask>\d+)\s+(?P<interface>.+?)\s+"
        r"((?P<admin_status>UP|DOWN)/(?P<oper_status>UP|DOWN)\s+)?"
        r"(?:Static|Dinamic|DHCP)\s",
        re.MULTILINE,
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
        r"((?P<members>.+?))?(^\s+Active bandwith is \d+Mbps\s*\n)?",
        re.MULTILINE | re.DOTALL,
    )
    rx_sh_int_des = rx_in = re.compile(
        r"^(?P<ifname>\S+)\s+(?:(?:General|Trunk|Access|Customer)(?: \(\d+\))?\s+)?(?P<oper_status>Up|Down)\s+"
        r"(?P<admin_status>Up|Down|Not Present)\s(?:(?P<descr>.*?)\n)?",
        re.MULTILINE,
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

    rx_slot_splitter = re.compile(r"\S+\s*(\d+)\/(\d+)\/(\d+)")

    def filter_interface(self, ifindex: int, name: str, oper_status: bool) -> bool:
        if self.is_3124:
            # Return More That ifaces on devices
            if name.startswith("Fa"):
                return False
            if name.startswith("Vl") and not oper_status:
                return False
            if name.startswith("Tu") and not oper_status:
                return False
        if self._chassis_filter and self.rx_slot_splitter.match(name):
            chassis, slot, port = self.rx_slot_splitter.match(name).groups()
            if chassis not in self._chassis_filter:
                return False
        return not (
            (name.startswith("Vl") or name.startswith("Lo"))
            and self.vlan_filter
            and ifindex not in self.vlan_filter
        )

    # if ascii or rus text in description
    def convert_description(self, desc):
        if desc:
            return smart_bytes(smart_text(desc, errors="replace"))
        return desc

    def get_ip_ifindex(self):
        r = set()
        for _, ifindex in self.snmp.getnext(
            mib["RFC1213-MIB::ipAdEntIfIndex"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
        ):
            r.add(ifindex)
        return r

    def get_stack_ifindex(self):
        # get ifindex stack interfaces
        # RADLAN-MIB::rlCascadeNeighborIfIndex 1.3.6.1.4.1.89.53.23.1.1
        # RADLAN-MIB::rlPhdUnitStackPortRow  1.3.6.1.4.1.89.53.25.1.1
        name_ifindex = {}
        stack_ifindex = set()
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.89.53.23.1.1"):
            stack_ifindex.add(oid[len("1.3.6.1.4.1.89.53.23.1.1") + 1 :])
        for oid, iface in self.snmp.getnext("1.3.6.1.4.1.89.53.25.1.1"):
            ifindex = oid[len("1.3.6.1.4.1.89.53.23.1.1") + 1 :].split(".")
            if ifindex[1] in stack_ifindex:
                sname = self.profile.convert_interface_name(
                    f"{iface[0:2]}{ifindex[0]}/0/{iface[-1]}"
                )
                sm = str(self.snmp.get(mib["IF-MIB::ifPhysAddress", int(ifindex[1])]))
                smac = MACAddressParameter().clean(sm)
                name_ifindex[sname] = {"sifindex": ifindex[1], "smac": smac}
        return name_ifindex

    def execute_snmp(self, **kwargs):
        # Stack numbers for filter
        self._chassis_filter = None
        if self.is_3124:
            if (
                "Stack | Member Ids" in self.capabilities
                and self.capabilities["Stack | Member Ids"] != "0"
            ):
                self._chassis_filter = set(self.capabilities["Stack | Member Ids"].split(" | "))
            self.logger.debug("Chassis members filter: %s", self._chassis_filter)
        self.vlan_filter = self.get_ip_ifindex()
        self.logger.info("Use Vlan filter: %s", self.vlan_filter)
        interfaces = super().execute_snmp()
        d = self.get_stack_ifindex()
        for name in d:
            sub = {
                "name": self.profile.convert_interface_name(name),
                "admin_status": "Up",
                "oper_status": "Up",
                "enabled_afi": [],
                "snmp_ifindex": d[name]["sifindex"],
                "mac": d[name]["smac"],
            }
            iface = {
                "type": self.profile.get_interface_type(name),
                "name": name,
                "admin_status": "Up",
                "oper_status": "Up",
                "enabled_protocols": [],
                "snmp_ifindex": d[name]["sifindex"],
                "mac": d[name]["smac"],
                "subinterfaces": [sub],
            }
            interfaces[0]["interfaces"] += [iface]
        return interfaces

    def execute(self, **kwargs):
        if self.is_3124:
            # Model 3124/3124F high CPU utilization if use CLI
            self.always_prefer = "S"
        return super().execute()

    def execute_cli(self):
        d = {}
        if self.has_snmp():
            try:
                for s in self.snmp.getnext("1.3.6.1.2.1.2.2.1.2", max_repetitions=10):
                    n = s[1]
                    sifindex = s[0][len("1.3.6.1.2.1.2.2.1.2") + 1 :]
                    if int(sifindex) < 3000:
                        sm = str(self.snmp.get(mib["IF-MIB::ifPhysAddress", int(sifindex)]))
                        smac = MACAddressParameter().clean(sm)
                        if n.startswith("oob"):
                            continue
                        sname = self.profile.convert_interface_name(n)
                    else:
                        continue
                    d[sname] = {"sifindex": sifindex, "smac": smac}
                if self.has_capability("Stack | Members"):
                    d = {**d, **self.get_stack_ifindex()}
            except self.snmp.TimeOutError:
                pass
        # Get portchannels
        portchannel_members = {}
        if self.has_capability("Network | LACP"):
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
        # Get stack interfaces
        if self.has_capability("Stack | Members"):
            for iface in parse_table(self.cli("show stack links details"), allow_wrap=True):
                i.append((f"{iface[1][0:2]}{iface[0]}/0/{iface[1][-1]}", "Up"))
        interfaces = []
        mtu = None
        for res in i:
            mac = None
            ifindex = 0
            name = res[0].strip()
            if self.is_has_chgroup:
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
                        if description:
                            description = description.strip()
                        else:
                            description = ""
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
                "enabled_afi": [],
            }
            if description:
                sub["description"] = description
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
                "enabled_protocols": [],
                "subinterfaces": [sub],
            }
            if description:
                iface["description"] = description
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
                ip = ip + "/" + netmask
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
            ip = ip + "/" + netmask
            ip_list = [ip]
            enabled_afi = []
            if ":" in ip:
                ip_interfaces = "ipv6_addresses"
                enabled_afi += ["IPv6"]
            else:
                ip_interfaces = "ipv4_addresses"
                enabled_afi += ["IPv4"]
            if ifname.startswith("vlan"):
                vlan = ifname.split(" ")[1]
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
                ],
            }
            interfaces += [iface]

        return [{"interfaces": interfaces}]
