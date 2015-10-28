# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_oam_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetoamstatus import IGetOAMStatus


class Script(BaseScript):
    name = "Juniper.JUNOS.get_oam_status"
    interface = IGetOAMStatus

    rx_line = re.compile(r"^  Interface:\s+", re.MULTILINE)
    rx_interface = re.compile(r"^(?P<interface>\S+)", re.MULTILINE)
    rx_mac = re.compile(
        r"^\s+(?P<mac>[0-9a-f]{2}\:[0-9a-f]{2}\:[0-9a-f]{2}\:"
        r"[0-9a-f]{2}\:[0-9a-f]{2}\:[0-9a-f]{2})", re.MULTILINE)
    rx_capsU = re.compile(
        r"Unidirection mode: (?P<caps_U>supported|unsupported)",
        re.IGNORECASE | re.MULTILINE)
    rx_capsR = re.compile(
        r"Remote loopback mode: (?P<caps_R>supported|unsupported)",
        re.IGNORECASE | re.MULTILINE)
    rx_capsL = re.compile(
        r"Link events: (?P<caps_L>supported|unsupported)",
        re.IGNORECASE | re.MULTILINE)
    rx_capsV = re.compile(
        r"Variable requests: (?P<caps_V>supported|unsupported)",
        re.IGNORECASE | re.MULTILINE)

    def execute(self, **kwargs):
        r = []
        try:
            v = self.cli("show oam ethernet link-fault-management detail")
        except self.CLISyntaxError:
            raise self.NotSupportedError
        for s in self.rx_line.split(v)[1:]:
            match = self.rx_interface.search(s)
            if not match:
                continue
            iface = match.group("interface")
            match = self.rx_mac.search(s)
            if not match:
                continue
            mac = match.group("mac")
            caps = []
            match = self.rx_capsR.search(s)
            if match and match.group("caps_R") == "supported":
                caps += ["R"]
            match = self.rx_capsU.search(s)
            if match and match.group("caps_U") == "supported":
                caps += ["U"]
            match = self.rx_capsL.search(s)
            if match and match.group("caps_L") == "supported":
                caps += ["L"]
            match = self.rx_capsV.search(s)
            if match and match.group("caps_V") == "supported":
                caps += ["V"]
            r += [{
                "interface": iface,
                "remote_mac": mac,
                "caps": caps
            }]
        return r
