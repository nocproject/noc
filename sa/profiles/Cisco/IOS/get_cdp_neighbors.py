# ---------------------------------------------------------------------
# Cisco.IOS.get_cdp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcdpneighbors import IGetCDPNeighbors
from noc.core.comp import smart_text
from noc.core.mib import mib


class Script(BaseScript):
    name = "Cisco.IOS.get_cdp_neighbors"
    interface = IGetCDPNeighbors
    always_prefer = "S"
    rx_entry = re.compile(
        r"Device ID: (?P<device_id>\S+).+? IP address: (?P<remote_ip>\S+).+?"
        r"Interface: (?P<local_interface>\S+),\s+Port ID \(outgoing port\): "
        r"(?P<remote_interface>\S+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    # oid_cdp = "1.3.6.1.4.1.9.9.23.1.2.1.1"
    oid_cdp = mib["CISCO-CDP-MIB::cdpCacheEntry"]
    rx_serial_check = re.compile(r"(\S+)\(\S+\)$")

    def execute_snmp(self, **kwargs):
        device_id = self.scripts.get_fqdn()
        # Get neighbors
        neighbors = []
        # Get interface status
        res = {}
        vif = self.snmp.get_table(mib["IF-MIB::ifName"])
        r = self.snmp.getnext(self.oid_cdp)
        loid = len(self.oid_cdp) + 1
        for v, dv in r:
            f, j, jo = v[loid:].split(".")
            res.setdefault((vif[int(j)], jo), {})[f] = dv
        for ii in res:
            try:
                r_device_id = smart_text(res[ii]["6"], errors="replace")
                # check if "()" in device_id and platform starts with "N", then clear out
                if self.rx_serial_check.match(r_device_id) and res[ii]["8"].startswith("N"):
                    r_device_id = self.rx_serial_check.match(r_device_id).group(1)
                ifname = self.profile.convert_interface_name(ii[0])
                # Convert `Se 0/0/0:0` to `Se 0/0/0`
                name, *sub = n.rsplit(":", 1)
                if sub:
                    ifname = name
                neighbors += [
                    {
                        "device_id": r_device_id,
                        "local_interface": ifname,
                        "remote_interface": res[ii]["7"],
                        "platform": res[ii]["8"],
                    }
                ]
                try:
                    if res[ii]["4"]:
                        msg = res[ii]["4"]
                        neighbors[-1]["remote_ip"] = "%d.%d.%d.%d" % (
                            ord(msg[0]),
                            ord(msg[1]),
                            ord(msg[2]),
                            ord(msg[3]),
                        )
                except (IndexError, ValueError):
                    pass
            except self.CLISyntaxError:
                pass
        return {"device_id": device_id, "neighbors": neighbors}

    def execute_cli(self, **kwargs):
        device_id = self.scripts.get_fqdn()
        # Get neighbors
        neighbors = []
        for match in self.rx_entry.finditer(self.cli("show cdp neighbors detail")):
            neighbors += [
                {
                    "device_id": match.group("device_id"),
                    "local_interface": match.group("local_interface"),
                    "remote_interface": match.group("remote_interface"),
                    "remote_ip": match.group("remote_ip"),
                }
            ]
        return {"device_id": device_id, "neighbors": neighbors}
