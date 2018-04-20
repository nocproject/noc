# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Juniper.JUNOS.get_chassis_id"
    cache = True
    interface = IGetChassisID
=======
##----------------------------------------------------------------------
## Juniper.JUNOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
from noc.lib.mac import MAC


class Script(NOCScript):
    name = "Juniper.JUNOS.get_chassis_id"
    cache = True
    implements = [IGetChassisID]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_range = re.compile(
        "(?P<type>Public|Private) base address\s+(?P<mac>\S+)\s+"
        "(?P=type) count\s+(?P<count>\d+)",
        re.DOTALL | re.IGNORECASE
    )
<<<<<<< HEAD
    rx_range2 = re.compile(
        r"^\s+Base address\s+(?P<mac>\S+)\s*\n"
        r"^\s+Count\s+(?P<count>\d+)",
        re.MULTILINE
    )

    def execute_cli(self):
        v = self.cli("show chassis mac-addresses")
        macs = []
        for f, t in [
            (mac, MAC(mac).shift(int(count) - 1))
            for _, mac, count in self.rx_range.findall(v)
        ]:
=======

    def execute(self):
        v = self.cli("show chassis mac-addresses")
        macs = []
        for f, t in [(mac, MAC(mac).shift(int(count) - 1))
                for _, mac, count in self.rx_range.findall(v)]:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            if macs and MAC(f).shift(-1) == macs[-1][1]:
                macs[-1][1] = t
            else:
                macs += [[f, t]]
<<<<<<< HEAD
        # Found in some oldest switches
        if macs == []:
            match = self.rx_range2.search(v)
            base = match.group("mac")
            count = int(match.group("count"))
            return [{
                "first_chassis_mac": base,
                "last_chassis_mac": MAC(base).shift(count - 1)
            }]
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return [
            {
                "first_chassis_mac": f,
                "last_chassis_mac": t
            } for f, t in macs
        ]
