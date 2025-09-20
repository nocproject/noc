# ---------------------------------------------------------------------
# DLink.DxS.get_oam_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetoamstatus import IGetOAMStatus


class Script(BaseScript):
    name = "DLink.DxS.get_oam_status"
    interface = IGetOAMStatus

    rx_line = re.compile(r"Port\s+", re.MULTILINE)
    rx_line1 = re.compile(r"\nRemote Client", re.MULTILINE)
    rx_oam = re.compile(r"\s+OAM\s+:\s+Enable", re.MULTILINE | re.IGNORECASE)
    rx_capsR = re.compile(
        r"\n\s+Remote Loopback\s+:\s+(?P<caps_R>\S+)", re.IGNORECASE | re.MULTILINE
    )
    rx_capsU = re.compile(r"\n\s+Unidirection\s+:\s+(?P<caps_U>\S+)", re.IGNORECASE | re.MULTILINE)
    rx_capsL = re.compile(
        r"\n\s+Link Monitoring\s+:\s+(?P<caps_L>\S+)", re.IGNORECASE | re.MULTILINE
    )
    rx_capsV = re.compile(
        r"\n\s+Variable Request\s+:\s+(?P<caps_V>\S+)", re.IGNORECASE | re.MULTILINE
    )

    rx_port = re.compile(r"^(?P<port>\S+)", re.MULTILINE)
    rx_mac = re.compile(r"\s+MAC Address\s+:\s+(?P<mac>\S+)", re.IGNORECASE | re.MULTILINE)

    def execute_cli(self, **kwargs):
        r = []
        try:
            v = self.cli("show ethernet_oam ports status")
        except self.CLISyntaxError:
            try:
                v = self.cli("show ethernet_oam ports all status")
            except self.CLISyntaxError:
                raise self.NotSupportedError
        for s in self.rx_line.split(v)[1:]:
            match = self.rx_line1.search(s)
            if match:
                match = self.rx_port.search(s)
            if match:
                iface = match.group("port").strip()
            for s1 in self.rx_line1.split(s)[1:]:
                match = self.rx_mac.search(s1)
                mac = match.group("mac")
                if mac == "-":
                    continue
                caps = []
                capsR = ""
                capsU = ""
                capsL = ""
                capsV = ""
                match = self.rx_capsR.search(s1)
                if match:
                    capsR = match.group("caps_R")
                match = self.rx_capsU.search(s1)
                if match:
                    capsU = match.group("caps_U")
                match = self.rx_capsL.search(s1)
                if match:
                    capsL = match.group("caps_L")
                match = self.rx_capsV.search(s1)
                if match:
                    capsV = match.group("caps_V")
                if "Supported" in capsR:
                    caps += ["R"]
                if "Supported" in capsU:
                    caps += ["U"]
                if "Support" in capsL:
                    caps += ["L"]
                if "Supported" in capsV:
                    caps += ["V"]
                r += [{"interface": iface, "remote_mac": mac, "caps": caps}]
        return r
