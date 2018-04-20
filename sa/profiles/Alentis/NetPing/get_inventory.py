# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Alentis.NetPing.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Alentis.NetPing.get_inventory"
    interface = IGetInventory
=======
##----------------------------------------------------------------------
## Alentis.NetPing.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInventory


class Script(NOCScript):
    name = "Alentis.NetPing.get_inventory"
    implements = [IGetInventory]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    cache = True

    rx_snmp = re.compile(
        r"^(?P<platform>\S+), FW \S+$")

    rx_plat = re.compile(
        r"^var devname='+(?P<platform>.+)+';$",
        re.MULTILINE)

    rx_rev = re.compile(
        r"^var hwmodel=\d+;var hwver=+(?P<revision>\d+)+;",
        re.MULTILINE)

    def execute(self):
        # Try SNMP first
<<<<<<< HEAD
        if self.has_snmp():
=======
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                ver = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                match = self.rx_snmp.search(ver)
                return [{
                    "type": "CHASSIS",
                    "number": "1",
                    "vendor": "Alentis",
                    "part_no": [match.group("platform")]
                }]
            except self.snmp.TimeOutError:
                pass

        # Fallback to HTTP
<<<<<<< HEAD
        response = self.http.get("/devname.cgi")
        match = self.rx_plat.search(response.body)
        platform = match.group("platform")
        match = self.rx_rev.search(response.body)
=======
        data = self.http.get("/devname.cgi")
        match = self.rx_plat.search(data)
        platform = match.group("platform")
        match = self.rx_rev.search(data)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        revision = match.group("revision")

        data = self.profile.var_data(self, "/setup_get.cgi")

        return [{
            "type": "CHASSIS",
            "number": "1",
            "builtin": False,
            "vendor": "Alentis",
            "part_no": [platform],
            "revision": revision,
            "serial": data["serialnum"],
            "description": data["location"].encode('UTF8')
        }]
