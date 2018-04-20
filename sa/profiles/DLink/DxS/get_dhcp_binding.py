# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS.get_dhcp_binding
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdhcpbinding import IGetDHCPBinding
=======
##----------------------------------------------------------------------
## DLink.DxS.get_dhcp_binding
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetDHCPBinding
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re
import datetime
import time


<<<<<<< HEAD
class Script(BaseScript):
    name = "DLink.DxS.get_dhcp_binding"
    interface = IGetDHCPBinding
=======
class Script(NOCScript):
    name = "DLink.DxS.get_dhcp_binding"
    implements = [IGetDHCPBinding]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(r"^(?P<name>\S+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>\S+)\s+(?P<type>Ethernet)\s+(?P<status>Automatic|Manual)\s+(?P<expire>.+?).*$", re.IGNORECASE | re.MULTILINE)

    def execute(self):
        try:
            data = self.cli("show dhcp_binding")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        for match in self.rx_line.finditer(data.lower()):
            d = match.group("expire")
            if d == "infinite":
                expire = d
            else:
                expire = datetime.datetime.fromtimestamp(time.time() + int(d))
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "expiration": expire,
                "type": match.group("status")[0].upper(),
            }]
        return r
