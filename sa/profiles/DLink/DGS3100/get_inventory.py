# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
 
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError

class Script(NOCScript):
    name = "DLink.DGS3100.get_inventory"
    implements = [IGetInventory]

    rx_dev = re.compile(
        r"Device Type\s+:\s+(?P<part_no>\S+).+Boot PROM Version\s+:\s+"
        r"(?:Build\s+)?(?P<bootprom>\S+).+Hardware Version\s+:\s+"
        r"(?P<revision>\S+)", re.MULTILINE | re.DOTALL)
    rx_ser = re.compile(
        r"Serial Number\s+:\s+(?P<serial>.+)\nSystem Name",
        re.MULTILINE | re.DOTALL)
    rx_des = re.compile(r"Device Type\s+:\s+(?P<descr>.+?)\n")

    def execute(self):
        s = self.cli("show switch", cached=True)
        match = self.rx_dev.search(s)
        part_no = match.group("part_no")
        revision = match.group("revision")
        serial = self.rx_ser.search(s).group("serial")
        description = self.rx_des.search(s).group("descr")

        r = [{
            "type": "CHASSIS",
            "number": "1",
            "vendor": "DLINK",
            "part_no": [part_no],
            "revision": revision,
            "serial": serial,
            "description": description
        }]
        return r
