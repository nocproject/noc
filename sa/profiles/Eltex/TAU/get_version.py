# ---------------------------------------------------------------------
# Eltex.TAU.get_version
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
    name = "Eltex.TAU.get_version"
    interface = IGetVersion
    cache = True
    always_prefer = "C"

    rx_ver = re.compile(
        r"^(?P<platform>\S+)\s*.+\n"
        r"System version:\s+#(?P<sysver>\S+)\n"
        r"\S.+\nFirmware\sversion:\s+(?P<fwver>\S+)",
        re.MULTILINE,
    )
    rx_shell_platform = re.compile(
        r"^Factory type: (?P<platform>\S+)\s*\S*\n^Factory SN:\s+(?P<serial>\S+)", re.MULTILINE
    )
    rx_shell_platform_tau4 = re.compile(
        r"^Board: (?P<platform>\S+)\s*\n"
        r"^HW Rev: (?P<hardware>\S+)\s*\n"
        r"^Serial: (?P<serial>\S+)",
        re.MULTILINE,
    )
    rx_shell_platform_tau8 = re.compile(r"^(?P<platform>\S+)$")
    rx_shell_serial_tau8 = re.compile(r"^(?P<serial>\S+)$")
    rx_shell_platform_a = re.compile(r"^(?P<platform>\S+)\s+PLD\s+(?P<serial>\S+)", re.MULTILINE)
    rx_shell_version = re.compile(r"^#?(?P<version>\S+)")
    rx_shell_fwversion = re.compile(r"^(?P<fwversion>[v\d]\S+)(?:\[)?", re.MULTILINE)
    rx_snmp_version = re.compile(r"^#(?P<version>\S+)$")

    # Working only on TAU-36 and above
    def execute_snmp(self):
        platform = self.snmp.get("1.3.6.1.4.1.35265.4.14.0", cached=True)
        v = self.snmp.get("1.3.6.1.4.1.35265.4.5.0", cached=True)
        match = self.rx_snmp_version.search(v)
        version = match.group("version")
        serial = self.snmp.get("1.3.6.1.4.1.35265.4.3.0", cached=True)
        hardware = self.snmp.get("1.3.6.1.4.1.35265.4.12.0", cached=True)
        return {
            "vendor": "Eltex",
            "platform": platform,
            "version": version,
            "attributes": {"FW version": hardware, "Serial Number": serial},
        }

    def execute_cli(self):
        v = self.cli("cat /version", cached=True)
        match = self.rx_shell_version.search(v)
        version = match.group("version")

        v = self.cli("cat /tmp/factory", cached=True)
        if "No such file or directory" not in v:
            if v != "":
                match = self.rx_shell_platform.search(v)
            else:
                v = self.cli("cat /tmp/arm_version; echo", cached=True)
                match = self.rx_shell_platform_a.search(v)
            platform = match.group("platform")
            serial = match.group("serial")
            v = self.cli("cat /tmp/msp_version; echo", cached=True)
            match = self.rx_shell_fwversion.search(v)
            fwversion = match.group("fwversion")
            return {
                "vendor": "Eltex",
                "platform": platform,
                "version": version,
                "attributes": {"FW version": fwversion, "Serial Number": serial},
            }
        v = self.cli("cat /tmp/.board_desc", cached=True)
        if "No such file or directory" not in v:
            match = self.rx_shell_platform_tau4.search(v)
            platform = match.group("platform")
            serial = match.group("serial")
            hardware = match.group("hardware")
            return {
                "vendor": "Eltex",
                "platform": platform,
                "version": version,
                "attributes": {"HW version": hardware, "Serial Number": serial},
            }
        v = self.cli("cat /tmp/board_type", cached=True)
        if "No such file or directory" not in v:
            match = self.rx_shell_platform_tau8.search(v)
            platform = match.group("platform")
            v = self.cli("cat /tmp/board_serial", cached=True)
            match = self.rx_shell_serial_tau8.search(v)
            serial = match.group("serial")
            return {
                "vendor": "Eltex",
                "platform": platform,
                "version": version,
                "attributes": {"Serial Number": serial},
            }
        raise self.NotSupportedError()
