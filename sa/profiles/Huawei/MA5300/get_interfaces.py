# ---------------------------------------------------------------------
# Huawei.MA5300.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Huawei.MA5300.get_interfaces"
    interface = IGetInterfaces
    keep_cli_session = False

    rx_iface_sep = re.compile(r"^ Vlan ID", re.MULTILINE | re.IGNORECASE)
    rx_vlan_id = re.compile(r"^: (?P<vlanid>\d+)$", re.MULTILINE | re.IGNORECASE)

    rx_iface = re.compile(r"^(?P<port>\S+\d+) is (?P<admin_state>up|down)", re.MULTILINE)
    rx_adsl_state = re.compile(r"^\s*(?P<port>Adsl\d+/\d+/\d+)\s+(?P<state>up|down)", re.MULTILINE)
    rx_vdsl_state = re.compile(r"^\s*(?P<port>Vdsl\d+/\d+/\d+)\s+(?P<state>up|down)", re.MULTILINE)
    rx_adsl_line = re.compile(
        r"^\s*(?P<port>Adsl\d+/\d+/\d+)\s+\d+\s+\d+\s+(?P<vpi>\d+|-)\s+(?P<vci>\d+|-)\s+",
        re.MULTILINE,
    )
    rx_vlan = re.compile(r"Vlan ID:\s+(?P<vlan_id>\d+)")
    rx_port = re.compile(r"(?P<port>(?:Adsl|Ethernet|GigabitEthernet)\d+/\d+/\d+)")
    rx_snmp = re.compile(
        r"^(?:Adsl|Ethernet|GigabitEthernet)(?P<card>\d+)/\d+/(?P<port>\d+)", re.MULTILINE
    )
    rx_tagged = re.compile(
        r"^\s*(?:Description:.+?)?(?:Route Interface: (?:not )?configured\s*)?.*?Tagged\s+Ports:(?P<tagged>.+)Untagged",
        re.MULTILINE | re.DOTALL,
    )
    rx_untagged = re.compile(r"\s+Untagged\s+Ports:(?P<untagged>.+)", re.MULTILINE | re.DOTALL)
    rx_ip_iface = re.compile(
        r"^\s*(?P<iface>\S+\d+) is (?P<admin_state>up|down),\s*"
        r"line protocol is (?P<oper_state>up|down)",
        re.MULTILINE,
    )
    rx_ip = re.compile(r"^\s*Internet Address is (?P<ip>\d+\S+\d+)", re.MULTILINE)
    rx_mtu = re.compile(r"^\s*The Maximum Transmit Unit is (?P<mtu>\d+)", re.MULTILINE)
    rx_mac = re.compile(r"Hardware address is (?P<mac>\S+)")

    def execute(self):
        interfaces = []
        vlan_table = []
        for vlan_entry in self.cli("show vlan all").split("\n\n"):
            match = self.rx_vlan.search(vlan_entry)
            if not match:
                break
            vlan = {"vlan_id": match.group("vlan_id"), "tagged": [], "untagged": []}
            match = self.rx_tagged.search(vlan_entry)
            for v in self.rx_port.finditer(match.group("tagged")):
                vlan["tagged"] += [v.group("port")]
            match = self.rx_untagged.search(vlan_entry)
            for v in self.rx_port.finditer(match.group("untagged")):
                if v != "none":
                    # Found on SmartAX MA5300 V100R006 VRP Version V3R000M03
                    # Tagged   Ports:
                    #             Ethernet7/2/0 Untagged Ports: none
                    vlan["untagged"] += [v.group("port")]
            vlan_table += [vlan]
        # ADSL ports state
        adsl_state = {}
        v = self.cli("show adsl port state all")
        for match in self.rx_adsl_state.finditer(v):
            adsl_state[match.group("port")] = match.group("state")

        # VDSL ports state
        """
        vdsl_state = {}
        v = self.cli("show vdsl port state all")
        for match in self.rx_vdsl_state.finditer(v):
            vdsl_state[match.group("port")] = match.group("state")
        """
        adsl_line = []
        v = self.cli("show adsl line config all")
        for match in self.rx_adsl_line.finditer(v):
            adsl_line += [match.groupdict()]
        v = self.cli("show interface")
        for match in self.rx_iface.finditer(v):
            name = match.group("port")
            # description = match.group("descr").strip()
            sub = {
                "name": name,
                "admin_status": True,
                "oper_status": True,
                "enabled_afi": ["BRIDGE"],
            }
            if "Adsl" in name:
                sub["enabled_afi"] += ["ATM"]
                if adsl_state.get(name):
                    sub["oper_status"] = adsl_state.get(name) == "up"
                for line in adsl_line:
                    if line["port"] == name:
                        if line["vpi"] != "-":
                            sub["vpi"] = line["vpi"]
                        if line["vci"] != "-":
                            sub["vci"] = line["vci"]
                        break
            for vlan in vlan_table:
                if name in vlan["tagged"]:
                    if "tagged_vlans" not in sub:
                        sub["tagged_vlans"] = []
                    sub["tagged_vlans"] += [vlan["vlan_id"]]
                if name in vlan["untagged"]:
                    sub["untagged_vlan"] = vlan["vlan_id"]
            iface = {
                "name": name,
                "type": "physical",
                "admin_status": True,
                "oper_status": sub["oper_status"],
                "subinterfaces": [sub],
            }
            """
            if description:
                iface["description"] = description
                iface["subinterfaces"][0]["description"] = description
            """
            match = self.rx_snmp.search(name)
            if match:
                if name.startswith("Adsl"):
                    snmp_ifindex = (
                        201326592 + int(match.group("card")) * 65536 + int(match.group("port")) * 64
                    )
                if name.startswith("Ethernet"):
                    snmp_ifindex = (
                        469762306 + int(match.group("card")) * 65536 + int(match.group("port")) * 64
                    )
                if name.startswith("Gigabit"):
                    snmp_ifindex = (
                        503316993 + int(match.group("card")) * 65536 + int(match.group("port")) * 64
                    )
                iface["snmp_ifindex"] = snmp_ifindex
            interfaces += [iface]
        for v in self.cli("show ip interface\n").split("\n\n"):
            match = self.rx_ip_iface.search(v)
            if not match:
                continue
            ifname = match.group("iface")
            c = self.cli("show interface %s" % ifname, ignore_errors=True)
            match1 = self.rx_mac.search(c)
            if match1:
                mac = match1.group("mac")
            else:
                mac = ""
            iface = {
                "name": ifname,
                "type": self.profile.get_interface_type(ifname),
                "admin_state": match.group("admin_state") == "up",
                "oper_state": match.group("oper_state") == "up",
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_state": match.group("admin_state") == "up",
                        "oper_state": match.group("oper_state") == "up",
                    }
                ],
            }
            if ifname.startswith("Vlan-interface"):
                iface["subinterfaces"][0]["vlan_ids"] = ifname[14:]
            match = self.rx_ip.search(v)
            if match:
                iface["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
                iface["subinterfaces"][0]["ipv4_addresses"] = [match.group("ip")]
            match = self.rx_mtu.search(v)
            if match:
                iface["subinterfaces"][0]["mtu"] = match.group("mtu")
            if mac:
                iface["mac"] = mac
                iface["subinterfaces"][0]["mac"] = mac
            interfaces += [iface]
        return [{"interfaces": interfaces}]
