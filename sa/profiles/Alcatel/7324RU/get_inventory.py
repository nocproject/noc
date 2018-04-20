# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.7324RU.get_inventory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError

class Script(BaseScript):
    name = "Alcatel.7324RU.get_inventory"
    interface = IGetInventory
=======
##----------------------------------------------------------------------
## Alcatel.7324RU.get_inventory
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
    name = "Alcatel.7324RU.get_inventory"
    implements = [IGetInventory]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_info = re.compile(r"Model:\s+7324\sRU\s(?P<hw1>\S+)\n.+Hardware\s"
        r"version:\s+(?P<hw2>\w+)\n\s+Serial\snumber:\s(?P<serial>\w+)",
        re.DOTALL)

    def execute(self):
        s = self.cli("sys info show", cached=True)
        match = self.rx_info.search(s)
        r = [{
            "type": "CHASSIS",
            "vendor": 'ALU',
            "part_no": ["7324RU"],
            "number": None,
            "serial": match.group("serial"),
            "revision": match.group("hw1") + " " + match.group("hw2")
        }]

        return r
