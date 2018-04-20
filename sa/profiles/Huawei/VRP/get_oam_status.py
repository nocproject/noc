# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------
# Huawei.VRP.get_oam_status
# ---------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetoamstatus import IGetOAMStatus
from noc.sa.interfaces.base import MACAddressParameter


class Script(BaseScript):
    name = "Huawei.VRP.get_oam_status"
    interface = IGetOAMStatus
=======
##----------------------------------------------------------------
## Huawei.VRP.get_oam_status
##----------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetOAMStatus
from noc.sa.interfaces.base import MACAddressParameter


class Script(NOCScript):
    name = "Huawei.VRP.get_oam_status"
    implements = [IGetOAMStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_line = re.compile(r"""
    \s+Interface:\s+(?P<interface>.+?)\n
    .+?
    Remote\sMAC:\s+(?P<mac>.+?)\n
    """, re.VERBOSE | re.DOTALL | re.MULTILINE)
    oam_splitter = re.compile(r"\s+-{52}(?P<oam>.+?)Remote\sEFM",
         re.DOTALL | re.MULTILINE)

    def execute(self, **kwargs):
        r = []
        try:
            v = self.cli("display efm all")
        except self.CLISyntaxError:
            raise self.NotSupportedError
        oams = re.findall(self.oam_splitter, v)
        if not oams:
<<<<<<< HEAD
            return []
=======
            raise self.NotSupportedError
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        for l in oams:
            match = self.rx_line.match(l)
            if match:
                iface = match.group("interface").strip()
                mac = match.group("mac")
                try:
                    mac=MACAddressParameter().clean(mac)
                except:
                   continue
                r += [{
                    "interface": iface,
                    "remote_mac": mac,
                    "caps": ["L"]
                }]
<<<<<<< HEAD
        return r
=======
        return r
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
