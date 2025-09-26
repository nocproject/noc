# ---------------------------------------------------------------------
# Raisecom.ROS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import ranges_to_list
from noc.core.ip import IPv4
from noc.core.mib import mib


class Script(BaseScript):
    name = "Raisecom.ROS.get_interfaces"
    interface = IGetInterfaces

    rx_vlans = re.compile(
        r"^\s*(?:Interface: |: |Port: )?(?P<name>\d+|gigaethernet1/1/\d+)\s*\n"
        r"(^\s*Switch Mode: switch\n)?"
        r"(^\s*Reject frame type: \S+\n)?"
        r"^\s*Administrative\sMode:\s*(?P<adm_mode>.*)\n"
        r"^\s*Operational\sMode:\s*(?P<op_mode>.*)\n"
        r"^\s*Access\sMode\sVLAN:\s*(?P<untagged_vlan>.*)\n"
        r"^\s*Administrative\sAccess\sEgress\sVLANs:\s*(?P<mvr_vlan>.*)\n"
        r"^\s*Operational\sAccess\sEgress\sVLANs:\s*(?P<op_eg_vlan>.*)\n"
        r"^\s*Trunk(?:\sNative)?\sMode(?:\sNative)?\sVLAN:\s*(?P<trunk_native_vlan>.*)\n"
        r"(^\s*Trunk\sNative\sVLAN(?:\sStatus)?:\s*(?P<trunk_native_vlan_mode>.*)\n)?"
        r"^\s*Administrative\sTrunk\sAllowed\sVLANs:\s*(?P<adm_trunk_allowed_vlan>.*)\n"
        r"^\s*Operational\sTrunk\sAllowed\sVLANs:\s*(?P<op_trunk_allowed_vlan>.*)\n"
        r"^\s*Administrative\sTrunk\sUntagged\sVLANs:\s*(?P<adm_trunk_untagged_vlan>.*)\n"
        r"^\s*Operational\sTrunk\sUntagged\sVLANs:\s*(?P<op_trunk_untagged_vlan>.*)",
        re.MULTILINE,
    )
    rx_vlans_2924 = re.compile(
        r"^\s*(?:Interface: )?(?P<name>.*)\n"
        r"(^\s*Reject frame type: \S+\n)?"
        r"^\s*Administrative\sMode:\s*(?P<adm_mode>.*)\n"
        r"^\s*Operational\sMode:\s*(?P<op_mode>.*)\n"
        r"^\s*Access\sMode\sVLAN:\s*(?P<untagged_vlan>.*)\n"
        r"^\s*Administrative\sAccess\sEgress\sVLANs:\s*(?P<mvr_vlan>.*)\n"
        r"^\s*Operational\sAccess\sEgress\sVLANs:\s*(?P<op_eg_vlan>.*)\n"
        r"^\s*Trunk(?:\sNative)?\sMode(?:\sNative)?\sVLAN:\s*(?P<trunk_native_vlan>.*)\n"
        r"^\s*Administrative\sTrunk\sAllowed\sVLANs:\s*(?P<adm_trunk_allowed_vlan>.*)\n"
        r"^\s*Operational\sTrunk\sAllowed\sVLANs:\s*(?P<op_trunk_allowed_vlan>.*)\n"
        r"^\s*Administrative\sTrunk\sUntagged\sVLANs:\s*(?P<adm_trunk_untagged_vlan>.*)\n"
        r"^\s*Operational\sTrunk\sUntagged\sVLANs:\s*(?P<op_trunk_untagged_vlan>.*)",
        re.MULTILINE,
    )
    rx_vlan2 = re.compile(
        r"^VLAN ID:\s+(?P<vlan_id>\d+)\s*\n"
        r"^Name:\s+\S+\s*\n"
        r"^State:\s+active\s*\n"
        r"^Status:\s+static\s*\n"
        r"^Member-Port:\s+port-list(?P<ports>\S+)\s*\n"
        r"^Untag-Ports:(\s+port-list(?P<untagged>\S+))?\s*\n",
        re.MULTILINE,
    )

    rx_vlans_ip = re.compile(r"^\s*(?P<iface>\d+)\s+(?P<vlan_id>\d+|none)", re.MULTILINE)
    rx_iface = re.compile(
        r"^\s*(?P<iface>\d+)\s+(?P<ip>\d\S+)\s+(?P<mask>\d\S+)\s+"
        r"(?P<vid>\d+)\s+(?P<oper_status>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_iface2 = re.compile(
        r"^\s*(?P<iface>\d+)\s+(?P<ip>\d\S+)\s+(?P<mask>\d\S+)\s+" r"assigned\s+primary\s*\n",
        re.MULTILINE,
    )
    rx_lldp = re.compile(
        r"LLDP enable status:\s+enable.+\n" r"LLDP enable ports:\s+(?P<ports>\S+)\n", re.MULTILINE
    )
    rx_lldp_2924 = re.compile(
        r"LLDP enable status:\s+enable.+\n" r"LLDP enable ports:\s+P:(?P<ports>\S+)\n", re.MULTILINE
    )
    rx_lldp_iscom2624g = re.compile(r"^(?P<ifname>\S+)\s+enable\s+\S+\s*\n", re.MULTILINE)
    rx_descr = re.compile(r"^\s*(?P<port>port\d+)\s+(?P<descr>.+)\n", re.MULTILINE)
    rx_iface_description = re.compile(
        r"^\s*(?P<iface>\S+)\s+(?P<admin_status>UP|DOWN)\s+"
        r"(?P<oper_status>UP|DOWN)\s+(?P<descr>.+)\n",
        re.MULTILINE,
    )
    rx_iface_iscom2624g = re.compile(
        r"^\s*(?P<ifname>\S+) is (?P<oper_status>UP|DOWN), "
        r"administrative status is (?P<admin_status>UP|DOWN)\s*\n"
        r"(^\s*Description is \"(?P<descr>.+)\",?\s*\n)?"
        r"(^\s*Hardware is (?P<hw_type>\S+), MAC address is (?P<mac>\S+)\s*\n)?"
        r"(^\s*Internet Address is (?P<ip>\S+)\s+primary\s*\n)?"
        r"(^\s*Internet v6 Address is (?P<ipv6>\S+)\s+Link\s*\n)?"
        r"(^\s*MTU (?P<mtu>\d+) bytes\s*\n)?",
        re.MULTILINE,
    )
    rx_ifunit = re.compile(r"\D+(?P<ifunit>\d+\S*)")

    IFTYPES = {
        "gigaethernet": "physical",
        "fastethernet": "physical",
        "vlan-interface": "SVI",
        "null": "null",
        "loopback": "loopback",
        "trunk": "aggregated",
        "unknown": "unknown",
    }

    def parse_vlans(self, section):
        r = {}
        if self.is_iscom2924g:
            match = self.rx_vlans_2924.search(section)
        else:
            match = self.rx_vlans.search(section)
        if match:
            r = match.groupdict()
        return r

    def get_bridge_ifindex_mappings(self):
        """
        Getting mappings for bridge port number -> ifindex
        :return:
        """
        pid_ifindex_mappings = {}
        for oid, v in self.snmp.getnext(
            mib["IF-MIB::ifIndex"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
            timeout=self.get_snmp_timeout(),
        ):
            pid_ifindex_mappings[int(oid.split(".")[-1])] = v
        return pid_ifindex_mappings

    def get_lldp_config(self):
        r = {}
        try:
            v = self.cli("show lldp local config")
        except self.CLISyntaxError:
            return r
        if self.is_iscom2924g:
            match = self.rx_lldp_2924.search(v)
        else:
            match = self.rx_lldp.search(v)
        if match:
            r = {el for el in self.expand_rangelist(match.group("ports"))}
        return r

    def get_switchport_cli(self):
        r = {}
        if self.is_rotek or self.is_gazelle:
            return r
        if self.is_iscom2924g:
            v = self.cli("show interface port-list 1-28 switchport")
        else:
            v = self.cli("show interface port switchport")

        separator = "\n\n" if self.is_iscom2924g else "Port"
        for section in v.split(separator):
            if not section:
                continue
            port = self.parse_vlans(section)
            r[port["name"]] = port
        return r

    def get_iface_statuses(self):
        r = []
        try:
            if self.is_iscom2924g:
                v = self.cli("show interface port-list 1-28")
            else:
                v = self.cli("show interface port")
        except self.CLISyntaxError:
            return r
        first_table_line = 2 if self.is_iscom2924g else 5
        for line in v.splitlines()[first_table_line:]:
            # r[int(line[:6])] = {
            r += [
                {
                    "name": int(line[1:6]) if self.is_iscom2924g else int(line[:6]),
                    "admin_status": (
                        "enable" in line[6:13] if self.is_iscom2924g else "enable" in line[7:14]
                    ),
                    "oper_status": (
                        "up" in line[13:28] if self.is_iscom2924g else "up" in line[14:29]
                    ),
                }
            ]
        return r

    def get_iface_ip_description(self):
        r = {}
        try:
            v = self.cli("show interface ip description")
        except self.CLISyntaxError:
            return r
        for line in v.splitlines()[2:-1]:
            r[str(int(line[:9]))] = {"name": int(line[:9]), "description": str(line[9:])}
        return r

    def execute_iscom2624g(self):
        lldp_ifaces = []
        v = self.cli("show lldp local config")
        lldp_ifaces_raw = self.rx_lldp_iscom2624g.findall(v)
        for iface in lldp_ifaces_raw:
            lldp_ifaces += [self.profile.convert_interface_name(iface)]
        ifaces = []
        v = self.cli("show interface")
        for iface in v.split("\n\n"):
            if not iface:
                continue
            match = self.rx_iface_iscom2624g.search("%s\n" % iface)
            ifname = match.group("ifname")
            if match.group("hw_type"):
                hw_type = match.group("hw_type")
                if ifname.startswith("NULL") and hw_type == "unknown":
                    hw_type = "null"
            elif ifname.startswith("loopback"):
                hw_type = "loopback"
            i = {
                "name": ifname,
                "type": self.profile.get_interface_type(ifname),
                "admin_status": match.group("admin_status") == "UP",
                "oper_status": match.group("oper_status") == "UP",
            }
            sub = {
                "name": ifname,
                "admin_status": match.group("admin_status") == "UP",
                "oper_status": match.group("oper_status") == "UP",
                "enabled_afi": [],
            }
            if match.group("descr"):
                i["description"] = match.group("descr").strip('"')
                sub["description"] = match.group("descr").strip('"')
            if match.group("mac") and match.group("mac") != "0000.0000.0000":
                i["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            if match.group("mtu"):
                sub["mtu"] = match.group("mtu")
            if match.group("ip"):
                sub["ipv6_addresses"] = [match.group("ip")]
                sub["enabled_afi"] += ["IPv4"]
            if match.group("ipv6"):
                sub["ipv6_addresses"] = [match.group("ipv6")]
                sub["enabled_afi"] += ["IPv6"]
            if i["type"] == "physical":
                sub["enabled_afi"] += ["BRIDGE"]
                if ifname in lldp_ifaces:
                    i["enabled_protocols"] = ["LLDP"]
                match = self.rx_ifunit.search(ifname)
                ifunit = match.group("ifunit")
                try:
                    v = self.cli("show switchport interface %s %s" % (hw_type, ifunit))
                    vlans = self.parse_vlans(v)
                    if vlans["op_mode"] != "trunk":
                        sub["untagged_vlan"] = int(vlans["untagged_vlan"])
                    else:
                        sub["untagged_vlan"] = int(vlans["trunk_native_vlan"])
                        sub["tagged_vlans"] = self.expand_rangelist(vlans["op_trunk_allowed_vlan"])
                except self.CLISyntaxError:
                    pass
            if i["type"] == "SVI":
                match = self.rx_ifunit.search(ifname)
                ifunit = match.group("ifunit")
                sub["vlan_ids"] = [int(ifunit)]
            i["subinterfaces"] = [sub]
            ifaces += [i]
        return [{"interfaces": ifaces}]

    def execute_iscom2924g(self):
        lldp_ifaces = self.get_lldp_config()
        interfaces = {}
        try:
            v = self.cli("show interface port-list 1-28 description")
        except self.CLISyntaxError:
            raise NotImplementedError
        for line in v.splitlines()[2:-1]:
            ifname = int(line[1:8])

            interfaces[ifname] = {
                "name": ifname,
                "type": "physical",
                "snmp_ifindex": ifname,
                "subinterfaces": [],
            }
            if str(line[8:]).strip() != ("-" and "--"):
                interfaces[ifname]["description"] = str(line[8:]).strip()
            if ifname in lldp_ifaces:
                interfaces[ifname]["enabled_protocols"] = ["LLDP"]
        for port in self.get_iface_statuses():
            if port["name"] in interfaces:
                interfaces[port["name"]].update(port)
            else:
                interfaces[port["name"]] = port
        vlans = self.get_switchport_cli()
        for ifname in interfaces:
            port = interfaces[ifname]
            name = str(f'port{port["name"]}')
            port["subinterfaces"] = [
                {
                    "name": name,
                    "enabled_afi": ["BRIDGE"],
                    "admin_status": port["admin_status"],
                    "oper_status": port["oper_status"],
                    "tagged_vlans": [],
                }
            ]

            if name in vlans:
                port["subinterfaces"][0]["untagged_vlan"] = int(vlans[name]["untagged_vlan"])
                if "n/a" not in vlans[name]["op_trunk_allowed_vlan"]:
                    port["subinterfaces"][0]["tagged_vlans"] = ranges_to_list(
                        vlans[name]["op_trunk_allowed_vlan"]
                    )
            if "description" in port:
                port["subinterfaces"][0]["description"] = port["description"]

        v = self.scripts.get_chassis_id()
        mac = v[0]["first_chassis_mac"]
        try:
            v = self.cli("show interface ip")
        except self.CLISyntaxError:
            raise NotImplementedError
        if v is not None:
            for line in v.splitlines()[2:]:
                ifname, addr, mask, *_ = line.split()
                i = {
                    "name": "ip%s" % ifname,
                    "type": "SVI",
                    "mac": mac,
                    "enabled_protocols": [],
                    "subinterfaces": [
                        {"name": "ip%s" % ifname, "mac": mac, "enabled_afi": ["IPv4"]}
                    ],
                }
                ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
                i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                interfaces[i["name"]] = i

        return [{"interfaces": list(interfaces.values())}]

    def execute_cli(self):
        if self.is_iscom2624g:
            return self.execute_iscom2624g()
        if self.is_iscom2924g:
            return self.execute_iscom2924g()
        lldp_ifaces = self.get_lldp_config()
        interfaces = {}
        if not self.is_rotek and not self.is_gazelle:
            v = self.cli("show interface port description")
            for line in v.splitlines()[2:-1]:
                ifname = int(line[:8])
                interfaces[ifname] = {
                    "name": ifname,
                    "type": "physical",
                    "snmp_ifindex": int(line[:8]),
                    "subinterfaces": [],
                }
                if str(line[8:]) != "-":
                    interfaces[ifname]["description"] = str(line[8:])
                if ifname in lldp_ifaces:
                    interfaces[ifname]["enabled_protocols"] = ["LLDP"]
            for port in self.get_iface_statuses():
                if port["name"] in interfaces:
                    interfaces[port["name"]].update(port)
                else:
                    interfaces[port["name"]] = port
        vlans = self.get_switchport_cli()
        for ifname in interfaces:
            port = interfaces[ifname]
            name = str(port["name"])
            port["subinterfaces"] = [
                {
                    "name": name,
                    "enabled_afi": ["BRIDGE"],
                    "admin_status": port["admin_status"],
                    "oper_status": port["oper_status"],
                    "tagged_vlans": [],
                }
            ]
            if name in vlans:
                port["subinterfaces"][0]["untagged_vlan"] = int(vlans[name]["untagged_vlan"])
                if "n/a" not in vlans[name]["op_trunk_allowed_vlan"]:
                    port["subinterfaces"][0]["tagged_vlans"] = ranges_to_list(
                        vlans[name]["op_trunk_allowed_vlan"]
                    )
            if "description" in port:
                port["subinterfaces"][0]["description"] = port["description"]
        if not interfaces:
            v = self.cli("show interface description")
            for match in self.rx_descr.finditer(v):
                i = {
                    "name": match.group("port"),
                    "type": "physical",
                    "description": match.group("descr").strip(),
                    "enabled_protocols": [],
                    "subinterfaces": [
                        {
                            "name": match.group("port"),
                            "enabled_afi": [],
                            "description": match.group("descr").strip(),
                        }
                    ],
                }
                interfaces[i["name"]] = i
            v = self.cli("show vlan detail")
            for match in self.rx_vlan2.finditer(v):
                vlan_id = int(match.group("vlan_id"))
                ports = ranges_to_list(match.group("ports"))
                if match.group("untagged"):
                    untagged = ranges_to_list(match.group("untagged"))
                else:
                    untagged = []
                for p in ports:
                    p_name = "port%s" % p
                    if p_name in interfaces:
                        if p not in untagged:
                            if "tagged_vlans" in interfaces[p_name]["subinterfaces"][0]:
                                interfaces[p_name]["subinterfaces"][0]["tagged_vlans"] += [vlan_id]
                            else:
                                interfaces[p_name]["subinterfaces"][0]["tagged_vlans"] = [vlan_id]
                        else:
                            interfaces[p_name]["subinterfaces"][0]["untagged_vlan"] = vlan_id
            # Check vlans
            for iface in interfaces.values():
                if (
                    "tagged_vlans" in iface["subinterfaces"][0]
                    or "untagged_vlan" in iface["subinterfaces"][0]
                ):
                    iface["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
        ifdescr = self.get_iface_ip_description()
        v = self.scripts.get_chassis_id()
        mac = v[0]["first_chassis_mac"]
        # XXX: This is a dirty hack !!!
        # I do not know, how get ip interface MAC address
        if not self.is_rotek and not self.is_gazelle:
            try:
                v = self.cli("show interface ip")
            except self.CLISyntaxError:
                v = self.cli("show interface ip 0")
            for match in self.rx_iface.finditer(v):
                ifname = match.group("iface")
                i = {
                    "name": "ip%s" % ifname,
                    "type": "SVI",
                    "oper_status": match.group("oper_status") == "active",
                    "admin_status": match.group("oper_status") == "active",
                    "mac": mac,
                    "enabled_protocols": [],
                    "subinterfaces": [
                        {
                            "name": "ip%s" % ifname,
                            "oper_status": match.group("oper_status") == "active",
                            "admin_status": match.group("oper_status") == "active",
                            "mac": mac,
                            "vlan_ids": [int(match.group("vid"))],
                            "enabled_afi": ["IPv4"],
                        }
                    ],
                }
                addr = match.group("ip")
                mask = match.group("mask")
                ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
                i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                if ifname in ifdescr:
                    i["description"] = ifdescr[ifname]["description"]
                    i["subinterfaces"][0]["description"] = ifdescr[ifname]["description"]
                interfaces[i["name"]] = i
        try:
            v = self.cli("show ip interface brief")
        except self.CLISyntaxError:
            return [{"interfaces": list(interfaces.values())}]
        for match in self.rx_iface2.finditer(v):
            ifname = match.group("iface")
            i = {
                "name": "ip%s" % ifname,
                "type": "SVI",
                "mac": mac,
                "enabled_protocols": [],
                "subinterfaces": [{"name": "ip%s" % ifname, "mac": mac, "enabled_afi": ["IPv4"]}],
            }
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
            interfaces[i["name"]] = i
        if not self.is_rotek:
            v = self.cli("show interface ip vlan")
            for match in self.rx_vlans_ip.finditer(v):
                vlan_id = match.group("vlan_id")
                if vlan_id == "none":
                    continue
                ifname = "ip%s" % match.group("iface")
                for iname in interfaces:
                    if iname == ifname:
                        interfaces[ifname]["subinterfaces"][0]["vlan_ids"] = vlan_id
                        break
        return [{"interfaces": list(interfaces.values())}]
