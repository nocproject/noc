# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_inventory"
    interface = IGetInventory

    """
    DGS-3610#show slots 
      Dev Slot Port Max Ports Configured Module            Online Module                User Status  Software Status
      --- ---- ---- --------- ---------------------------- ---------------------------- ------------ ---------------
      1   0    24   24        N/A                          DGS-3610-26G                 N/A          ok             
      1   1    0    1         N/A                          none                         N/A          none           
      1   2    0    1         N/A                          none                         N/A          none    

    DGS-3610#show interfaces status 
    Interface                Status    Vlan  Duplex   Speed     Type  
    ------------------------ --------  ----  -------  --------- ------
    GigabitEthernet 0/1      up        1     Full     1000M     fiber
    GigabitEthernet 0/2      up        1     Full     1000M     fiber

    """
    rx_dev = re.compile(
        r"^\s+\d+\s+(?P<number>\d+)\s+\d+\s+\d+\s+\S+\s+(?P<part_no>\S+)",
        re.MULTILINE)
    rx_status = re.compile(
        r"^(?:Ten)?GigabitEthernet \d+/(?P<number>\d+)\s+(?:up|down)\s+\d+\s+"
        r"\S+\s+(?P<speed>1\d+M)\s+(?P<type>\S+)\s*\n", re.MULTILINE)

    def execute(self):
        r = []
        try:
            s = self.cli("show slots")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_dev.finditer(s):
            number = match.group("number")
            part_no = match.group("part_no")
            if part_no == "none":
                continue
            if number == '0':
                p = {
                    "type": "CHASSIS",
                    "vendor": "DLINK",
                    "part_no": [part_no]
                }
                v = self.scripts.get_version()
                if "HW version" in v["attributes"]:
                    p["revision"] = v["attributes"]["HW version"]
                if "Serial Number" in v["attributes"]:
                    p["serial"] = v["attributes"]["Serial Number"]
            else:
                p = {
                    "type": "MODULE",
                    "number": number,
                    "vendor": "DLINK",
                    "part_no": [part_no]
                }
            r += [p]
        s = self.cli("show interfaces status")
        for match in self.rx_status.finditer(s):
            if match.group("type") == "fiber":
                if match.group("speed") == "1000M":
                    r += [{
                        "type": "XCVR",
                        "number": match.group("number"),
                        "vendor": "NONAME",
                        "part_no": ["NoName | Transceiver | 1G | SFP"]
                    }]
                if match.group("speed") == "10000M":
                    r += [{
                        "type": "XCVR",
                        "number": match.group("number"),
                        "vendor": "NONAME",
                        "part_no": ["NoName | Transceiver | 10G | XFP"]
                    }]
        return r
