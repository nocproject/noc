# ---------------------------------------------------------------------
# DLink.DxS_Industrial_CLI.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "DLink.DxS_Industrial_CLI.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^\s*(?P<ifname>(?:Eth|vlan|mgmt_ipif |Port-channel)\S+) is (?P<admin_status>\S+),? (?:fiber |copper )?[Ll]ink status is (?P<oper_status>\S+)\s*\n"
        r"^\s*Interface type: \S+\s*\n"
        r"^\s*Interface description:(?P<descr>.*)\n"
        r"(^\s*MAC [Aa]ddress: (?P<mac>\S+)\s*\n)?",
        re.MULTILINE,
    )
    rx_mtu = re.compile(r"^\s*Maximum transmit unit: (?P<mtu>\d+) bytes", re.MULTILINE)
    rx_vlan = re.compile(
        r"^\s*VLAN (?P<vlan_id>\d+)\s*\n"
        r"^\s*Name\s*:\s+(?P<name>\S+)\s*\n"
        r"^\s*Tagged Member Ports\s*:(?P<tagged>.*)\n"
        r"^\s*Untagged Member Ports\s*:(?P<untagged>.*)\n",
        re.MULTILINE,
    )
    rx_portgroup_port = re.compile(r"^\s*(?P<port>[Ee]th\d+\S+)\s+", re.MULTILINE)
    rx_ip_iface = re.compile(
        r"^\s*(Interface )?(?P<ifname>(?:vlan|mgmt_ipif |loopback)\d+) is (?P<admin_status>\S+),(?: [Ll]ink status is (?P<oper_status>\S+))?\s*\n"
        r"(^\s*IP [Aa]ddress is (?P<ip>\S+).*)?\n?"
        r"(^\s*IP [Aa]ddress is (?P<ip2>\S+) \(Manual\) Secondary)?",
        re.MULTILINE,
    )
    rx_ip_mtu = re.compile(r"^\s*IP MTU is (?P<mtu>\d+) bytes\s*\n", re.MULTILINE)
    rx_ip_with_prefix = re.compile(r"\d+\.\d+\.\d+.\d+/\d+\.\d+\.\d+.\d+")

    def execute_cli(self):
        interfaces = []
        v = self.cli("show interfaces")
        has_if_range = False
        for line in v.split("\n\n"):
            match = self.rx_iface.search(line)
            if not match:
                continue
            ifname = match.group("ifname")
            i = {
                "name": ifname,
                "type": self.profile.get_interface_type(ifname),
                "admin_status": match.group("admin_status") == "enabled",
                "oper_status": match.group("oper_status") == "up",
                "mac": match.group("mac"),
                "enabled_protocols": [],
            }
            sub = {
                "name": ifname,
                "admin_status": match.group("admin_status") == "enabled",
                "oper_status": match.group("oper_status") == "up",
                "mac": match.group("mac"),
                "enabled_afi": ["BRIDGE"],
            }
            descr = match.group("descr").strip()
            if descr:
                i["description"] = descr
                sub["description"] = descr
            if i["type"] == "physical":
                if_range = "%s-%s" % (ifname[3:], ifname.split("/")[2])
                if not has_if_range:
                    try:
                        v1 = self.cli("show lldp interface %s | include Admin Status" % ifname)
                    except self.CLISyntaxError:
                        v1 = self.cli(
                            "show lldp interface ethernet %s | include Admin Status" % if_range
                        )
                        has_if_range = True
                else:
                    v1 = self.cli(
                        "show lldp interface ethernet %s | include Admin Status" % if_range
                    )
                if "TX and RX" in v1:
                    i["enabled_protocols"] += ["LLDP"]
            match = self.rx_mtu.search(line)
            sub["mtu"] = match.group("mtu")
            if i["type"] == "aggregated" and ifname.startswith("Port-channel"):
                portgroup = ifname[12:]
                v1 = self.cli("show channel-group channel %s detail" % portgroup)
                for match1 in self.rx_portgroup_port.finditer(v1):
                    port = self.profile.convert_interface_name(match1.group("port"))
                    for iface in interfaces:
                        if iface["name"] == port:
                            iface["aggregated_interface"] = ifname
                            break
                if "Protocol: LACP" in v1:
                    i["enabled_protocols"] += ["LACP"]
            i["subinterfaces"] = [sub]
            interfaces += [i]

        v = self.cli("show vlan", cached=True)
        for match in self.rx_vlan.finditer(v):
            vlan_id = match.group("vlan_id")
            tagged = self.expand_interface_range(match.group("tagged"))
            untagged = self.expand_interface_range(match.group("untagged"))
            for i in interfaces:
                sub = i["subinterfaces"][0]
                if i["name"][3:] in tagged:
                    if "tagged_vlans" in sub:
                        sub["tagged_vlans"] += [vlan_id]
                    else:
                        sub["tagged_vlans"] = [vlan_id]
                if i["name"][3:] in untagged:
                    sub["untagged_vlan"] = vlan_id

        v = self.cli("show ip interface")
        has_space = False
        for line in v.split("\n\n"):
            match = self.rx_ip_iface.search(line)
            if not match:
                continue
            ifname = match.group("ifname").replace(" ", "")
            if match.group("oper_status"):
                oper_status = match.group("oper_status") == "up"
            else:
                oper_status = True
            i = {
                "name": ifname,
                "type": self.profile.get_interface_type(ifname),
                "admin_status": match.group("admin_status") == "enabled",
                "oper_status": oper_status,
            }
            sub = {
                "name": ifname,
                "admin_status": match.group("admin_status") == "enabled",
                "oper_status": oper_status,
            }
            ip = match.group("ip")
            if ip:
                match1 = self.rx_ip_with_prefix.search(ip)
                if match1:
                    ip_address, ip_subnet = ip.split("/")
                    ip = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                sub["enabled_afi"] = ["IPv4"]
                sub["ipv4_addresses"] = [ip]
            ip = match.group("ip2")
            if ip:
                match1 = self.rx_ip_with_prefix.search(ip)
                if match1:
                    ip_address, ip_subnet = ip.split("/")
                    ip = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                sub["ipv4_addresses"] += [ip]
            if i["type"] == "SVI":
                sub["vlan_ids"] = (ifname[4:],)
            match1 = self.rx_ip_mtu.search(line)
            if match1:
                i["mtu"] = match1.group("mtu")
            if ifname.startswith("vlan"):
                ifname_with_space = "vlan %s" % ifname[4:]
            elif ifname.startswith("mgmt_ipif"):
                ifname_with_space = "mgmt %s" % ifname[9:]
            elif ifname.startswith("lopback"):
                ifname_with_space = "loopback %s" % ifname[8:]
            elif ifname.startswith("Null"):
                ifname_with_space = "Null %s" % ifname[4:]
            if not has_space:
                try:
                    v1 = self.cli("show interface %s" % ifname)
                except self.CLISyntaxError:
                    v1 = self.cli("show interface %s" % ifname_with_space)
                    has_space = True
                else:
                    v1 = self.cli("show interface %s" % ifname_with_space)
            match1 = self.rx_iface.search(v1)
            descr = match1.group("descr").strip()
            if descr:
                i["description"] = descr
                sub["description"] = descr
            if match1.group("mac"):
                i["mac"] = match1.group("mac")
                sub["mac"] = match1.group("mac")
            i["subinterfaces"] = [sub]
            interfaces += [i]

        # TODO: show ipv6 interface

        return [{"interfaces": interfaces}]
