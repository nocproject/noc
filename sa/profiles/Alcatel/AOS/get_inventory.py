# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(NOCScript):
    name = "Alcatel.AOS.get_inventory"
    implements = [IGetInventory]
    rx_ni = re.compile(
    r"^\s+GBIC\s+(?P<int_number>\d+)\n"
    r"\s+Manufacturer Name:\s+(?P<vendor>\S+)(|\s+),\n"
    r"^\s+Part Number:\s+(?P<part_number>\S+)(|\s+),\n"
    r"^\s+Hardware Revision:\s+(|(?P<hw_rev>\S+))(|\s+),\n"
    r"^\s+Serial Number:\s+(?P<serial>\S+)(|\s+)(|\s+),\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)
                                                    
    def execute(self):
        objects = []
        #Chassis info
        p = self.scripts.get_version()
        objects += [{
            "type": "CHASSIS",
            "number": None,
            "vendor": "ALU",
            "serial": p["attributes"].get("Serial Number"),
            "description": p["vendor"] + " " + p["platform"],
            "part_no": p["platform"],
            "revision": p["attributes"].get("HW version"),
            "builtin": False
        }]
        #Transiver Detected
        iface = self.cli("show ni")
        for match in self.rx_ni.finditer(iface):
            number = match.group("int_number")
#           type = match.group("int")
            vendor = match.group("vendor")
            serial = match.group("serial")
            hw_rev = match.group("hw_rev")
            if not hw_rev:
                hw_rev = "None"
            part_no = match.group("part_number")
            if "XFP-10G-LR" in part_no:
                part = "NoName | Transceiver | 10G | XFP LR"
            elif "SFP-LX" in part_no:
                part = "NoName | Transceiver | 1G | SFP LX"
            elif "SFP-LH" in part_no:
                part = "NoName | Transceiver | 1G | SFP LH"
            elif "GLC-BX" in part_no:
                part = "Cisco | Transceiver | 1G | GLC-BX-D"
                vendor = "Cisco"
            else:
                part = "NoName | Transceiver | 1G | SFP SX"
            objects += [{
                "type": "XCVR",
                "number": number,
                "vendor": "NONAME",
                "serial": serial,
                "description": "SFP Transceiver " + part_no,
                "part_no": [part],
                "revision": hw_rev,
                "builtin": False
                }]
                                                                                                                                                                                                                                                                                                
        return objects
