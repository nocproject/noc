# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
 
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


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
    """
    rx_dev = re.compile(
        r"^\s+\d+\s+(?P<number>\d+)\s+\d+\s+\d+\s+\S+\s+(?P<part_no>\S+)",
        re.MULTILINE | re.DOTALL)

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
                    "number": "1",
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

        return r
