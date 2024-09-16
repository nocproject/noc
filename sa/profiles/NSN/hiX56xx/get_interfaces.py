# ---------------------------------------------------------------------
# NSN.hiX56xx.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
import re


class Script(BaseScript):
    name = "NSN.hiX56xx.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^\s*(?P<port>\d+/\d+)\s+(?P<vlan_id>\d+)\s+"
        r"(?P<admin_status>Up|Dwn|-)/(?P<oper_status>Up|Dwn)",
        re.MULTILINE,
    )
    rx_port_stat = re.compile(
        r"^\s+ifIndex\s+(?P<snmp_ifindex>\d+)\s*\n"
        r"^\s+ifDescr(?P<descr>.+)\n"
        r"^\s+ifType\s+(?P<iftype>\d+)\s*\n"
        r"^\s+ifMtu\s+(?P<mtu>\d+)\s*\n"
        r"^\s+ifSpeed\s+\d+\s*\n"
        r"^\s+ifPhysAddress\s+(?P<mac>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_port_name = re.compile(r"^\s+ifName\s+(?P<ifname>\S+)\s*\n", re.MULTILINE)
    rx_vlan = re.compile(r"^\s+(\d+\s+)?\|(?P<vlans>.*)\n", re.MULTILINE)
    rx_ifname_sub = re.compile(r"^(?P<ifname>\d+/\d+)/(?P<sub>\d+)$")
    rx_line = re.compile(
        r"^(?P<ifname>\d+/\d+)?\s+(?P<sub>\d+)\s+"
        r"(?P<admin_status>\S+)\s+(?P<vpi>\d+)\s+(?P<vci>\d+)\s+llc",
        re.MULTILINE,
    )
    rx_interface = re.compile(  # "index" do not correlate with "snmp_ifindex"
        r"^(?:Interface )?(?P<ifname>\S+)\s*\n"
        r"^\s+Hardware is \S+(, address is (?P<mac>\S+))?\s*\n"
        r"^\s+index \d+ metric \d+ mtu (?P<mtu>\d+) <(?P<flags>\S+)>\s*\n"
        r"^\s+VRF Binding: (?P<vrf>.+)\n",
        re.MULTILINE,
    )
    rx_ip = re.compile(r"^\s+inet (?P<ip>\S+) broadcast \S+\s*\n", re.MULTILINE)

    def execute(self):
        interfaces = []
        port_map = {}

        v = self.cli("show port", cached=True)  # used in get_mac_address_table
        for match in self.rx_port.finditer(v):
            if match.group("admin_status") == "-":
                iftype = "aggregated"
                admin_status = True
            else:
                iftype = "physical"
                admin_status = match.group("admin_status") == "Up"
            iface = {
                "name": match.group("port"),
                "type": iftype,
                "admin_status": admin_status,
                "oper_status": match.group("oper_status") == "Up",
                "subinterfaces": [
                    {
                        "name": match.group("port"),
                        "admin_status": admin_status,
                        "oper_status": match.group("oper_status") == "Up",
                        "enabled_afi": ["BRIDGE"],
                        "untagged_vlan": match.group("vlan_id"),
                        "tagged_vlans": [],
                    }
                ],
            }
            interfaces += [iface]

        for i in interfaces:
            sub = i["subinterfaces"][0]
            v = self.cli(
                "show port statistics interface %s" % i["name"],
                cached=True,  # used in get_mac_address_table
            )
            match = self.rx_port_stat.search(v)
            i["snmp_ifindex"] = match.group("snmp_ifindex")
            if match.group("descr").strip():
                i["description"] = match.group("descr").strip()
                sub["description"] = match.group("descr").strip()
            sub["mtu"] = match.group("mtu")
            if match.group("mac") != "00:00:00:00:00:00":
                i["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            match = self.rx_port_name.search(v)
            port_map[i["name"]] = match.group("ifname")

        for vlans in self.scripts.get_vlans():
            vlan_id = vlans["vlan_id"]
            v = self.cli("show vlan %s" % vlan_id)
            for match in self.rx_vlan.finditer(v):
                vlan_list = match.group("vlans").strip()
                if not vlan_list or vlan_list.startswith("locked by"):
                    continue
                for i in vlan_list.split(","):
                    if i.strip() == "":
                        continue
                    vlan_type = i[-1:]
                    ifname = i[:-1]
                    match1 = self.rx_ifname_sub.search(ifname)
                    if match1:
                        ifname1 = match1.group("ifname")
                        sub = {
                            "name": ifname,
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "vlan_ids": [vlan_id],
                        }
                        for iface in interfaces:
                            if iface["name"] == ifname1:
                                iface["subinterfaces"] += [sub]
                                break
                        else:
                            interfaces += [
                                {"name": ifname1, "type": "physical", "subinterfaces": [sub]}
                            ]
                    else:
                        for iface in interfaces:
                            if iface["name"] == ifname:
                                sub = iface["subinterfaces"][0]
                                if vlan_type == "u":
                                    sub["untagged_vlan"] = vlan_id
                                elif "tagged" in sub:
                                    sub["tagged_vlans"] += [vlan_id]
                                else:
                                    sub["tagged_vlans"] = [vlan_id]
                                break
                        else:
                            iface = {"name": ifname, "type": "physical"}
                            sub = {"name": ifname}
                            if vlan_type == "u":
                                sub["untagged_vlan"] = vlan_id
                            else:
                                sub["tagged_vlans"] = [vlan_id]
                            iface["subinterfaces"] = [sub]
                            interfaces += [iface]

        # Do not use range s1-s10 due to high CPU utilization
        for s in range(0, 11):
            v = self.cli("show lre s%s xdsl atm vcctp-info" % s)
            for match in self.rx_line.finditer(v):
                if match.group("ifname"):
                    ifname = match.group("ifname")
                    old_port = ifname
                else:
                    ifname = old_port
                # Normalize ifname from "01/01" to "1/1"
                ifname = "/".join([str(int(x)) for x in ifname.split("/")])
                subname = "%s/%s" % (ifname, match.group("sub"))
                for i in interfaces:
                    if i["name"] == ifname:
                        for sub in i["subinterfaces"]:
                            if sub["name"] == subname:
                                sub["admin_status"] = match.group("admin_status") == "enabled"
                                sub["vpi"] = match.group("vpi")
                                sub["vci"] = match.group("vci")
                                break
                        break

        v = self.cli("show interface")
        for p in v.split("\nInterface "):
            match = self.rx_interface.search(p)
            if not match:
                continue
            ifname = match.group("ifname")
            iface = {
                "name": ifname,
                "admin_status": "UP," in match.group("flags"),
                "oper_status": "UP," in match.group("flags"),
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": "UP," in match.group("flags"),
                        "oper_status": "UP," in match.group("flags"),
                        "mtu": match.group("mtu"),
                    }
                ],
            }
            sub = iface["subinterfaces"][0]
            if ifname.startswith("lo"):
                iface["type"] = "loopback"
            elif ifname.startswith("mgmt"):
                iface["type"] = "management"
            elif ifname.startswith("br"):
                iface["type"] = "SVI"
                sub["vlan_ids"] = [int(ifname[2:])]
            else:
                raise self.NotSupportedError()
            if match.group("mac"):
                iface["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            match = self.rx_ip.search(p)
            if match:
                sub["enabled_afi"] = ["IPv4"]
                sub["ipv4_addreses"] = [match.group("ip")]
            interfaces += [iface]

        # Set interface's names according to ifName
        for i in interfaces:
            if i["name"] in port_map:
                new_name = port_map[i["name"]]
                i["name"] = new_name
                i["subinterfaces"][0]["name"] = new_name

        return [{"interfaces": interfaces}]
