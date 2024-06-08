# ---------------------------------------------------------------------
# BDCOM_xPON.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
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
        r"(^\s+protocolstatus.+\n)?"
        r"^\s+Ifindex is (?P<snmp_ifindex>\d+)(, unique port number is \d+)?\s*\n"
        r"(^\s+Description: (?P<descr>.+)\n)?"
        r"^\s+Hardware is (?P<type>\S+)(, [Aa]ddress is (?P<mac>\S+)\s*\(.+\))?\s*\n"
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
        "Giga-Combo-FX-SFP": "physical",  # GigabitEthernet Combo port
        "Giga-TX": "physical",  # GigabitEthernet
        "Giga-FX": "physical",  # GigabitEthernet
        "Giga-FX-SFP": "physical",  # GigabitEthernet
        "10Giga-FX": "physical",  # TGigaEthernet port
        "10Giga-FX-SFP": "physical",  # TGigaEthernet SFP port
        "10Giga-DAC": "physical",  # TGigaEthernet SFP+ DAC
        "GigaEthernet-PON": "physical",  # EPON port
        "GigaEthernet-LLID": "other",  # EPON ONU port
        "Giga-PON": "physical",  # EPON port
        "Giga-LLID": "other",  # EPON ONU port
        "GPON": "physical",  # GPON port
        "GPON-ONUID": "other",  # GPON ONU port
        "EtherSVI": "SVI",
        "PortAggregator": "aggregated",
        "Null": "null",
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
            }
            sub = {
                "name": ifname,
                "admin_status": "up" in match.group("admin_status"),
                "oper_status": "up" in match.group("oper_status"),
                "snmp_ifindex": match.group("snmp_ifindex"),
                "mtu": match.group("mtu"),
            }
            if match.group("mac"):
                i["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            if match.group("descr") and match.group("descr").strip():
                i["description"] = match.group("descr").strip()
                sub["description"] = match.group("descr").strip()
            if match.group("ip"):
                sub["enabled_afi"] = ["IPv4"]
                sub["ipv4_addresses"] = [match.group("ip")]
            if typ in ["GPON-ONUID", "Giga-LLID", "GigaEthernet-LLID"] and ":" in ifname:
                parent_iface = ifname.split(":")[0]
                for iface in ifaces:
                    if iface["name"] == parent_iface:
                        iface["subinterfaces"] += [sub]
                        break
                continue
            if i["type"] == "physical":
                sub["enabled_afi"] = ["BRIDGE"]
                # Do not remove this!
                # Some BDCOM OLT closing connection without empty line
                self.cli("")
                c = self.cli("show vlan interface %s" % match.group("ifname"))
                for r in parse_table(c, allow_wrap=True, n_row_delim=","):
                    if not is_int(r[2]):
                        continue
                    untagged = int(r[2])
                    sub["untagged_vlan"] = untagged
                    if r[3] != "none":
                        tagged = self.expand_rangelist(r[3])
                        tagged = [item for item in tagged if int(item) != untagged]
                        if tagged:
                            sub["tagged_vlans"] = tagged
            if i["type"] == "SVI":
                sub["vlan_ids"] = ifname[4:]
            if ifname.startswith("GigaEthernet") or ifname.startswith("TGigaEthernet"):
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
