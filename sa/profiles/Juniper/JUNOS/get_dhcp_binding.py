# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_dhcp_binding
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import datetime
import time
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdhcpbinding import IGetDHCPBinding


class Script(BaseScript):
    name = "Juniper.JUNOS.get_dhcp_binding"
    interface = IGetDHCPBinding

    rx_line = re.compile(
        r"^(?P<ip>\d+\.\d+\.\d+\.\d+)\s+\d+\s+(?P<mac>\S+)\s+"
        r"(?P<expires>\d+)\s+BOUND\s+\S+\s*$", re.IGNORECASE | re.MULTILINE)

    def execute(self):
        try:
            data = self.cli("show dhcp server binding")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        for match in self.rx_line.finditer(data):
            e = match.group("expires")
            expire = datetime.datetime.fromtimestamp(time.time() + int(e))
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "expiration": expire,
                "type": "A"
            }]
        return r
