# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_cdp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcdpneighbors import IGetCDPNeighbors
import re


class Script(BaseScript):
    name = "Cisco.IOS.get_cdp_neighbors"
    interface = IGetCDPNeighbors
    rx_entry = re.compile(
        r"Device ID: (?P<device_id>\S+).+? IP address: (?P<remote_ip>\S+).+?"
        r"Interface: (?P<local_interface>\S+),\s+Port ID \(outgoing port\): "
        r"(?P<remote_interface>\S+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    oid_cdp = "1.3.6.1.4.1.9.9.23.1.2.1.1"
    rx_serial_check = re.compile(r"(\S+)\(\S+\)$")

    def execute(self):
        device_id = self.scripts.get_fqdn()
        # Get neighbors
        neighbors = []
        if self.has_snmp():
            try:
                # Get interface status
                res = {}
                vif = self.snmp.get_table("1.3.6.1.2.1.31.1.1.1.1")
                r = self.snmp.getnext(self.oid_cdp)
                loid = len(self.oid_cdp) + 1
                for v, dv in r:
                    f, j, jo = v[loid:].split(".")
                    res.setdefault((vif[int(j)], jo), {})[f] = dv
                for ii in res:
                    try:
                        r_device_id = res[ii]["6"]
                        # check if "()" in device_id and platform starts with "N", then clear out
                        if self.rx_serial_check.match(r_device_id) and res[ii]["8"].startswith("N"):
                            r_device_id = self.rx_serial_check.match(r_device_id).group(1)
                        neighbors += [
                            {
                                "device_id": r_device_id,
                                "local_interface": self.profile.convert_interface_name(ii[0]),
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
            except self.snmp.TimeOutError:
                pass
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
