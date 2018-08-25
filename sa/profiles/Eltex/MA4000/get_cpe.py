# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_cpe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE


class Script(BaseScript):
    name = "Eltex.MA4000.get_cpe"
    interface = IGetCPE

    rx_cpe = re.compile(
        r"^\s+Serial number:\s+(?P<serial>\S+)\s*\n"
        r"^\s+Slot:\s+(?P<slot>\d+)\s*\n"
        r"^\s+Gpon password:\s+(?P<password>\S+)\s*\n"
        r"^\s+Gpon-port:\s+(?P<port>\d+)\s*\n"
        r"^\s+ONT ID:\s+(?P<ont_id>\d+)\s*\n"
        r"^\s+Equipment ID:\s+(?P<model>\S+)\s*\n"
        r"^\s+Hardware version:\s+(?P<hw_version>\S+)\s*\n"
        r"^\s+Software version:\s+(?P<sw_version>\S+)\s*\n"
        r"^\s+Equalization delay:\s+(?P<eq_delay>\S+)\s*\n"
        r"^\s+FEC state:\s+(?P<fec>\S+)\s*\n"
        r"^\s+OMCI port:\s+(?P<omci_port>\d+)\s*\n"
        r"^\s+Alloc IDs:\s+(?P<alloc_ids>.+)\s*\n"
        r"^\s+Hardware state:\s+(?P<hw_state>\S+)\s*\n"
        r"^\s+State:\s+(?P<state>\S+)\s*\n"
        r"^\s+ONT distance:\s+(?P<ont_dist>\S+).*\n"
        r"^\s+RSSI:\s+(?P<rssi>.+)\s*\n",
        re.MULTILINE
    )

    state_map = {
        "OK": "active",
        "CFGINPROGRESS": "provisioning"
    }

    def execute(self):
        r = []
        for slot in range(0, 16):
            c = self.cli("show interface ont %d/0-7/0-63 state" % slot)
            for match in self.rx_cpe.finditer(c):
                cpe_id = "ONT%s/%s/%s" % (
                    match.group("slot"),
                    match.group("port"),
                    match.group("ont_id")
                )
                r += [{
                    "id": cpe_id,
                    "global_id": match.group("serial"),
                    "status": self.state_map[match.group("state")],
                    "type": "ont",
                    "interface": "ont %s/%s/%s" % (
                        match.group("slot"),
                        match.group("port"),
                        match.group("ont_id")
                    ),
                    "model": match.group("model"),
                    "serial": match.group("serial"),
                    "version": match.group("sw_version"),
                    "distance": float(match.group("ont_dist")) * 1000
                }]

        return r
