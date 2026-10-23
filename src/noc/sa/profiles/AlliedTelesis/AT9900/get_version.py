# ---------------------------------------------------------------------
# AlliedTelesis.AT9900.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "AlliedTelesis.AT9900.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(
        r"^(Allied Telesis|x900-24XS) (?P<platform>AT[/\w-]+)(, | )version (?P<version>[\d.]+-[\d]+)",
        re.MULTILINE | re.DOTALL,
    )
    rx_serial = re.compile(
        r"^Base\s+\d+\s+(?P<platform>\S+)\s+\S+\s+(?P<hardware>\S+)\s+(?P<serial>\S+)",
        re.MULTILINE | re.DOTALL,
    )

    def execute_snmp(self):
        v = self.snmp.get("1.3.6.1.2.1.1.1.0")
        match = self.re_search(self.rx_ver, v)
        version = match.group("version")
        for board_num, board_name, board_hw, board_serial in self.snmp.get_tables(
            [
                "1.3.6.1.4.1.207.8.4.4.5.2.1.3",
                "1.3.6.1.4.1.207.8.4.4.5.2.1.4",
                "1.3.6.1.4.1.207.8.4.4.5.2.1.5",
            ],
            max_retries=1,
        ):
            if board_num == "1":
                return {
                    "vendor": "Allied Telesis",
                    "platform": board_name[board_name.find("AT-") :],
                    "version": version,
                    "attributes": {"HW version": board_hw.strip(), "Serial Number": board_serial},
                }

    def execute_cli(self):
        if self.has_snmp():
            try:
                pl = self.snmp.get("1.3.6.1.4.1.207.8.17.1.3.1.6.1")
                ver = self.snmp.get("1.3.6.1.4.1.207.8.17.1.3.1.5.1")
                if pl and ver:
                    return {
                        "vendor": "Allied Telesis",
                        "platform": pl,
                        "version": ver.lstrip("v"),
                    }
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show system")
        match = self.re_search(self.rx_ver, v)
        platform = match.group("platform")
        version = match.group("version")
        match = self.re_search(self.rx_serial, v)
        hardware = match.group("hardware")
        serial = match.group("serial")
        return {
            "vendor": "Allied Telesis",
            "platform": platform,
            "version": version,
            "attributes": {"HW version": hardware, "Serial Number": serial},
        }
