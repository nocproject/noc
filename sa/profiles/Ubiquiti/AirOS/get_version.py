# ---------------------------------------------------------------------
# Ubiquiti.AirOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.snmp.render import render_mac


class Script(BaseScript):
    name = "Ubiquiti.AirOS.get_version"
    cache = True
    interface = IGetVersion

    rx_version = re.compile(r"^(?P<prefix>\S+)\.\S+?\.(?P<version>(v\d+\.\d+.\d+))[\.\-]\S+$")

    def execute_cli(self):
        version = self.cli("cat /etc/version").strip()
        board = self.cli("grep board.name /etc/board.info").strip()
        board = board.split("=", 1)[1].strip()
        serial = self.cli("grep board.hwaddr /etc/board.info").strip()
        serial = serial.split("=", 1)[1].strip()
        return {
            "vendor": "Ubiquiti",
            "platform": board,
            "version": version,
            "attributes": {"Serial Number": serial},
        }

    def execute_snmp(self):
        try:
            platform = self.snmp.get("1.2.840.10036.3.1.2.1.3.5")
            version = self.snmp.get("1.2.840.10036.3.1.2.1.4.5")
            serial = self.snmp.get(
                "1.2.840.10036.2.1.1.1.5", display_hints={"1.2.840.10036.2.1.1.1.5": render_mac}
            )
        except self.snmp.SNMPError as e:
            # NO_SUCH_NAME
            if e.code == 2:
                platform = self.snmp.get("1.2.840.10036.3.1.2.1.3.8")
                version = self.snmp.get("1.2.840.10036.3.1.2.1.4.8")
                serial = self.snmp.get(
                    "1.2.840.10036.2.1.1.1.8", display_hints={"1.2.840.10036.2.1.1.1.5": render_mac}
                )
        except self.snmp.TimeOutError:
            raise self.UnexpectedResultError

        v_match = self.rx_version.search(version)
        version = v_match.group("prefix") + "." + v_match.group("version")
        serial = MACAddressParameter().clean(serial).replace(":", "").upper()
        return {
            "vendor": "Ubiquiti",
            "platform": platform,
            "version": version,
            "attributes": {"Serial Number": serial},
        }
