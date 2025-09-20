# ---------------------------------------------------------------------
# DLink.DxS.get_dhcp_binding
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import datetime
import time

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdhcpbinding import IGetDHCPBinding


class Script(BaseScript):
    name = "DLink.DxS.get_dhcp_binding"
    interface = IGetDHCPBinding
    rx_line = re.compile(
        r"^(?P<name>\S+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>\S+)\s+(?P<type>Ethernet)\s+(?P<status>Automatic|Manual)\s+(?P<expire>.+?).*$",
        re.IGNORECASE | re.MULTILINE,
    )

    def execute_cli(self):
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
            r += [
                {
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "expiration": expire,
                    "type": match.group("status")[0].upper(),
                }
            ]
        return r
