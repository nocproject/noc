# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# BDCOM_xPON.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import parse_table
from noc.core.validators import is_int


class Script(BaseScript):
    name = "BDCOM.xPON.get_interfaces"
    interface = IGetInterfaces
    TIMEOUT = 300

    rx_int = re.compile(
        r"^(?P<ifname>\S+\d+) is (?P<admin_status>up|down|administratively down), line protocol is (?P<oper_status>up|down)\s*\n"
        r"^\s+Ifindex is (?P<snmp_ifindex>\d+)(, unique port number is \d+)?\s*\n"
        r"(^\s+Description: (?P<descr>.+)\n)?"
        r"^\s+Hardware is (?P<type>\S+), [Aa]ddress is (?P<mac>\S+)\s*\(.+\)\s*\n"
        r"(^\s+Interface address is (?P<ip>\S+)\s*\n)?"
        r"^\s+MTU (?P<mtu>\d+) bytes",
        re.MULTILINE,
    )
    rx_lldp = re.compile(r"(?P<ifname>^\S+):\nRx: (?P<lldp_rx>\S+)\nTx: (?P<lldp_tx>\S+)")

    types = {
        "GigaEthernet-TX": "physical",  # GigabitEthernet
        "GigaEthernet-FX": "physical",  # GigabitEthernet
        "Giga-Combo-TX": "physical",  # GigabitEthernet Combo port
        "Giga-Combo-FX": "physical",  # GigabitEthernet Combo port
        "GigaEthernet-PON": "physical",  # EPON port
        "GigaEthernet-LLID": "other",  # EPON port
        "Giga-TX": "physical",  # GigabitEthernet
        "Giga-FX": "physical",  # GigabitEthernet
        "Giga-PON": "physical",  # EPON port
        "Giga-LLID": "other",  # EPON port
        "EtherSVI": "SVI",
    }

    # @todo: snmp
    # @todo: cdp
    # @todo: gvrp

    def execute_cli(self):
        ifaces = []
        v = self.cli("show interface")
        for match in self.rx_int.finditer(v):
            ifname = self.profile.convert_interface_name(match.group("ifname"))
            typ = match.group("type")
            iftype = self.types[typ]
            i = {
                "name": ifname,
                "type": iftype,
                "admin_status": "up" in match.group("admin_status"),
                "oper_status": "up" in match.group("oper_status"),
                "snmp_ifindex": match.group("snmp_ifindex"),
                "mac": match.group("mac"),
            }
            sub = {
                "name": ifname,
                "admin_status": "up" in match.group("admin_status"),
                "oper_status": "up" in match.group("oper_status"),
                "mac": match.group("mac"),
                "mtu": match.group("mtu"),
            }
            if match.group("descr") and match.group("descr").strip():
                i["description"] = match.group("descr").strip()
                sub["description"] = match.group("descr").strip()
            if match.group("ip"):
                sub["enabled_afi"] = ["IPv4"]
                sub["ipv4_addresses"] = [match.group("ip")]
            if i["type"] == "physical":
                sub["enabled_afi"] = ["BRIDGE"]
                c = self.cli("show vlan interface %s" % match.group("ifname"))
                for r in parse_table(c, allow_wrap=True, n_row_delim=","):
                    if is_int(r[2]):
                        untagged = int(r[2])
                        sub["untagged_vlan"] = untagged
                        tagged = self.expand_rangelist(r[3])
                        tagged = [item for item in tagged if int(item) != untagged]
                        if tagged:
                            sub["tagged_vlans"] = tagged
            if ifname.startswith("GigaEthernet"):
                cmd1 = "show lldp interface %s" % ifname
                cmd2 = self.cli(cmd1)
                for match1 in self.rx_lldp.finditer(cmd2):
                    if (
                        match1.group("lldp_rx") == "enabled"
                        or match1.groups("lldp_tx") == "enabled"
                    ):
                        i["enabled_protocols"] = ["LLDP"]
            i["subinterfaces"] = [sub]
            ifaces += [i]
        return [{"interfaces": ifaces}]
