# ---------------------------------------------------------------------
# Huawei.VRP.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Huawei.VRP.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_vrp3line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>Learned|Config static)\s+(?P<interfaces>[^ ]+)\s{2,}"
    )
    rx_vrp5line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)(?:\s+|/)\-\s+(?:\-\s+)?(?P<interfaces>\S+)\s+"
        r"(?P<type>dynamic|static|security|sticky|authen|sec-config)(?:\s+\-)?"
    )
    rx_vrp5_bd_line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)/\-/\-\s+(?P<interfaces>\S+)\s+"
        r"(?P<type>dynamic|static|security|sticky|authen|sec-config)"
    )
    rx_vrp53line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<interfaces>\S+)\s+"
        r"(?P<type>dynamic|static|security|sticky|authen|sec-config)\s+"
    )

    def execute_snmp(self, **kwargs):
        r = []
        interface_mappings = {
            x["ifindex"]: x["interface"]
            for x in self.scripts.get_interface_properties(enable_ifindex=True)
        }
        # hwDynFdbPort
        for oid, port in self.snmp.getnext(
            "1.3.6.1.4.1.2011.5.25.42.2.1.3.1.4", max_retries=1, max_repetitions=20, timeout=20
        ):
            mac, vlan_id, vid1, vid2 = oid.rsplit(".", 3)
            mac = ":".join("%02X" % int(x) for x in mac.split(".")[-6:])
            if int(vlan_id) == 0:
                self.logger.warning("[%s|%s] VLAN ids is 0", interface_mappings[port], mac)
                continue
            r += [
                {
                    "vlan_id": vlan_id,
                    "mac": mac,
                    "interfaces": [interface_mappings[port]],
                    "type": "D",
                }
            ]
        return r

    def execute_cli(self, interface=None, vlan=None, mac=None, **kwargs):
        cmd = "display mac-address"
        if mac is not None:
            cmd += " %s" % self.profile.convert_mac(mac)
        v = self.cli(cmd)
        version = self.profile.fix_version(self.scripts.get_version())
        if version.startswith("3"):
            rx_line = self.rx_vrp3line
        elif version.startswith("5.3"):
            rx_line = self.rx_vrp53line
        elif version.startswith("5"):
            # Found in S5720S-52X-SI-AC v 5.170 (V200R011C10SPC600)
            if "VLAN/VSI/BD" in v:
                rx_line = self.rx_vrp5_bd_line
            else:
                rx_line = self.rx_vrp5line
        else:
            rx_line = self.rx_vrp5line
        r = []
        for line in v.splitlines():
            match = rx_line.match(line.strip())
            if match:
                if vlan is not None and int(match.group("vlan_id")) != vlan:
                    continue
                if interface is not None and match.group("interfaces") != interface:
                    continue
                r += [
                    {
                        "vlan_id": match.group("vlan_id"),
                        "mac": match.group("mac"),
                        "interfaces": [match.group("interfaces")],
                        "type": {
                            "dynamic": "D",
                            "static": "S",
                            "learned": "D",
                            "config static": "S",
                            "security": "S",
                            "sticky": "S",
                            "authen": "D",
                            "sec-config": "S",
                        }[match.group("type").lower()],
                    }
                ]
        return r
