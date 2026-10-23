# ---------------------------------------------------------------------
# VyOS.VyOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import Any

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "VyOS.VyOS.get_interfaces"
    interface = IGetInterfaces

    rx_int = re.compile(
        r"^(?P<name>.+?):\s+<(?P<flags>.+?)> mtu (?P<mtu>\d+) .+state (?P<state>\S+)"
    )
    rx_descr = re.compile(r"^\s+Description:\s+(?P<descr>.+?)\s*$")
    rx_inet = re.compile(r"^\s+inet\s+(?P<inet>\S+)")
    rx_inet6 = re.compile(r"^\s+inet6\s+(?P<inet6>\S+)")
    rx_mac = re.compile(r"\s+link/ether\s+(?P<mac>\S+)")
    rx_ifindex = re.compile(r"^(?P<ifname>\S+):\s+ifIndex = (?P<ifindex>\d+)\n", re.MULTILINE)

    def get_ifindex(self) -> dict[str, int]:
        """
        Returns mapping of if name -> ifindex
        """
        out = self.cli("show snmp mib ifmib")
        return {
            match.group("ifname"): int(match.group("ifindex"))
            for match in self.rx_ifindex.finditer(out)
        }

    def execute_cli(self):
        def update_ifindex(x: dict[str, Any]) -> None:
            name = x.get("name")
            if not name:
                return
            ifindex = ifindexes.get(name)
            if ifindex is not None:
                x["snmp_ifindex"] = ifindex

        def append_to_sub(name: str, value: str) -> None:
            if r[-1]["subinterfaces"]:
                last_si = r[-1]["subinterfaces"][-1]
                if name in last_si:
                    last_si[name].append(value)
                else:
                    last_si[name] = [value]
            else:
                r[-1]["subinterfaces"] = [{"name": current_iface, name: [value]}]
                update_ifindex(r[-1]["subinterfaces"][-1])

        def ensure_afi(afi: str) -> None:
            sub = r[-1]["subinterfaces"][-1]
            enabled_afi = sub.get("enabled_afi", [])
            if afi not in enabled_afi:
                enabled_afi.append(afi)
            sub["enabled_afi"] = enabled_afi

        ifindexes = self.get_ifindex()
        r: list[dict[str, Any]] = []  # Result
        current_iface = ""
        is_vif = False
        out = self.cli("show interfaces detail", cached=True)
        for line in out.splitlines():
            if match := self.rx_int.search(line):
                # New interface, strip linux internal interface name after `@``
                current_iface = match.group("name").split("@", 1)[0]
                is_vif = "." in current_iface
                if is_vif:
                    r[-1]["subinterfaces"].append(
                        {"name": current_iface, "vlan_ids": [int(current_iface.rsplit(".", 1)[-1])]}
                    )
                    update_ifindex(r[-1]["subinterfaces"][-1])
                else:
                    r.append(
                        {
                            "name": current_iface,
                            "type": self.profile.get_interface_type(current_iface),
                            "mtu": int(match.group("mtu")),
                            "admin_status": ",UP," in match.group("flags"),
                            "oper_status": match.group("state") in ["UP", "UNKNOWN"],
                            "subinterfaces": [],
                        }
                    )
                    update_ifindex(r[-1])
            elif match := self.rx_descr.search(line):
                if is_vif:
                    r[-1]["subinterfaces"][-1]["descriptipn"] = match.group("descr")
                else:
                    r[-1]["description"] = match.group("descr")
            elif match := self.rx_mac.search(line):
                r[-1]["mac"] = match.group("mac")
            elif match := self.rx_inet.search(line):
                append_to_sub("ipv4_addresses", match.group("inet"))
                ensure_afi("IPv4")
            elif match := self.rx_inet6.search(line):
                append_to_sub("ipv6_addresses", match.group("inet6"))
                ensure_afi("IPv6")
        return [{"interfaces": r}]
