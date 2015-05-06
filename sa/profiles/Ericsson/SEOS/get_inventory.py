# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ericsson.SEOS.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(NOCScript):
    name = "Ericsson.SEOS.get_inventory"
    implements = [IGetInventory]

    rx_trans = re.compile(
        r"Port\s*:\s*(\S+)\s*XFP\s*\S+\s*Media\s*"
        r"Type\s*:\s*([A-Za-z0-9 \/]+)\s*"
        r"Redback\s*Approved\s*:\s*(YES|NO)\s*"
        r"Diagnostic\s*Monitoring\s*:\s*\S+\s*"
        r"CLEI\s*code\s*:\s*\S*\s*"
        r"Serial\s*Number\s*:\s*(\S+)\s*\S+\s*:\s*(\S*)",
        re.DOTALL | re.IGNORECASE | re.MULTILINE)

    def execute(self):
        objects = []
        v = self.cli("show hardware")
        media = self.cli("show port trans")
        for l in v.splitlines():
            if "backplane" in l:
                objects += [{
                    "builtin": False,
                    "description": "Chassis backplane",
                    "number": 0,
                    "part_no": "SE600",
                    "serial": l.split()[2].strip(),
                    "vendor": "Ericsson",
                    "type": "CHASSIS"
                }]
            elif "fan tray" in l:
                objects += [{
                    "builtin": False,
                    "description": "Fan Tray",
                    "number": 1,
                    "part_no": "SE600-FAN",
                    "serial": l.split()[3].strip(),
                    "vendor": "Ericsson",
                    "type": "FAN"
                }]
            elif "alarm card" in l:
                objects += [{
                    "builtin": False,
                    "description": "Alarm Card",
                    "number": 0,
                    "part_no": "SE600-ALARM",
                    "serial": l.split()[3].strip(),
                    "vendor": "Ericsson",
                    "type": "ALRM"
                }]
            elif "-port" in l:
                objects += [{
                    "builtin": False,
                    "description": l.split()[1].strip(),
                    "number": l.split()[0].strip(),
                    "part_no": l.split()[1].strip(),
                    "serial": l.split()[2].strip(),
                    "vendor": "Ericsson",
                    "type": "CARD"
                }]
                for match in self.rx_trans.findall(media):
                    if l.split()[0].strip() == match[0].split("/")[0]:
                        objects += [{
                            "builtin": False,
                            "description": match[1].strip() + " " +
                                           match[4].strip(),
                            "number": match[0][2:],
                            "part_no": match[1].strip(),
                            "serial": match[3],
                            "vendor": "NoName",
                            "type": "XCVR"
                        }]
            elif "xcrp" in l:
                objects += [{
                    "builtin": False,
                    "description": l.split()[1].strip(),
                    "number": l.split()[0].strip(),
                    "part_no": l.split()[1].strip(),
                    "serial": l.split()[2].strip(),
                    "vendor": "Ericsson",
                    "type": "MGMT"
                }]
        return objects

