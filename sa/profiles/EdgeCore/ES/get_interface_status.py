# ---------------------------------------------------------------------
# EdgeCore.ES.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.mib import mib


class Script(BaseScript):
    name = "EdgeCore.ES.get_interface_status"
    interface = IGetInterfaceStatus
    cache = True

    rx_interface_status = re.compile(
        r"^(?P<interface>.+?)\s+is\s+\S+,\s+"
        r"line\s+protocol\s+is\s+(?P<status>up|down).*?"
        r"index is (?P<ifindex>\d+).*?address is (?P<mac>\S+).*?",
        re.IGNORECASE | re.DOTALL,
    )
    rx_interface_descr = re.compile(
        r".*?alias name is (?P<descr>[^,]+?),.*?", re.IGNORECASE | re.DOTALL
    )
    rx_interface_status_3526 = re.compile(
        r"Information of (?P<interface>[^\n]+?)\n.*?"
        r"Mac Address(|\s+):\s+(?P<mac>[^\n]+?)\n(?P<block>.*)",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )
    rx_interface_intstatus_3526 = re.compile(
        r".*?Name(|\s+):[^\n]* (?P<descr>[^\n]*?)\n.*?"
        r"Link Status(|\s+):\s+(?P<intstatus>up|down)\n",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )
    rx_interface_linestatus_3526 = re.compile(
        r"Port Operation Status(|\s+):\s+(?P<linestatus>up|down)\n",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )
    rx_snmp_name_eth = re.compile(
        r"Ethernet Port on unit\s+(?P<unit>[^\n]+?),\s+" r"port(\s+|\:)(?P<port>\d{1,2})",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )

    def execute_snmp(self, interface=None):
        # Get interface status
        r = []
        for i, n, s, d, m in self.snmp.join(
            [
                mib["IF-MIB::ifDescr"],
                mib["IF-MIB::ifOperStatus"],
                mib["IF-MIB::ifAlias"],
                mib["IF-MIB::ifPhysAddress"],
            ],
            join="left",
        ):
            match = self.rx_snmp_name_eth.search(n)
            if match:
                if match.group("unit") == "0":
                    unit = "1"
                    n = "Eth " + unit + "/" + match.group("port")
                else:
                    n = "Eth " + match.group("unit") + "/" + match.group("port")
            if n.startswith("Trunk ID"):
                n = "Trunk " + n.replace("Trunk ID ", "").lstrip("0")
            if n.startswith("Trunk Port ID"):
                n = "Trunk " + n.replace("Trunk Port ID ", "").lstrip("0")
            if n.startswith("Trunk Member"):
                n = "Eth 1/" + str(i)
            if n.startswith("VLAN ID"):
                n = "VLAN " + n.replace("VLAN ID ", "").lstrip("0")
            if n.startswith("VLAN interface"):
                n = "VLAN " + n.replace("VLAN interface ID ", "").lstrip("0")
            if n.startswith("Console"):
                continue
            if n.startswith("Loopback"):
                continue
            r += [
                {
                    "snmp_ifindex": i,
                    "interface": n,
                    "status": int(s) == 1,
                    "description": d,
                    "mac": MACAddressParameter().clean(m),
                }
            ]
        return r

    def execute_cli(self, interface=None):
        r = []
        if self.is_platform_4626:
            try:
                cmd = "show interface status | include line protocol is|alias|address is"
                buf = self.cli(cmd).replace("\n ", " ")
            except Exception:
                cmd = "show interface status"
                buf = self.cli(cmd, cached=True).replace("\n ", " ")
            for l in buf.splitlines():
                match = self.rx_interface_status.match(l)
                if match:
                    r += [
                        {
                            "interface": match.group("interface"),
                            "status": match.group("status") == "up",
                            "mac": MACAddressParameter().clean(match.group("mac")),
                            "snmp_ifindex": match.group("ifindex"),
                        }
                    ]
                    mdescr = self.rx_interface_descr.match(l)
                    if mdescr:
                        r[-1]["description"] = mdescr.group("descr")
        else:
            cmd = "show interface status"
            buf = self.cli(cmd, cached=True).lstrip("\n\n")
            for l in buf.split("\n\n"):
                match = self.rx_interface_status_3526.search(l + "\n")
                if match:
                    descr = ""
                    interface = match.group("interface")
                    if interface.startswith("VLAN"):
                        linestatus = "up"
                    elif match.group("block"):
                        block = match.group("block")
                        submatch = self.rx_interface_intstatus_3526.search(block)
                        if submatch:
                            descr = submatch.group("descr")
                        linestatus = "down"
                        submatch = self.rx_interface_linestatus_3526.search(block)
                        if submatch:
                            linestatus = submatch.group("linestatus").lower()
                    r += [
                        {
                            "interface": interface,
                            "mac": MACAddressParameter().clean(match.group("mac")),
                            "status": linestatus.lower() == "up",
                        }
                    ]
                    if descr:
                        r[-1]["description"] = descr
        return r
