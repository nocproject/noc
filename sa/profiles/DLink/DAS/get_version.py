# ---------------------------------------------------------------------
# DLink.DAS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Tuple
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "DLink.DAS.get_version"
    cache = True
    interface = IGetVersion

    rx_descr = re.compile(r"Description\s+: (?P<platform>\S+)")
    rx_vendor = re.compile(r"Vendor\s+: (?P<vendor>\S+)")
    rx_serial = re.compile(r"SN\s+: S/N: (?P<serial>\S+)")
    rx_hardware = re.compile(r"HW_Ver\s+: H/W Ver. : (?P<hardware>.+)\n")
    rx_ver = re.compile(
        r"^Object-id\s+: (?P<sys_oid>\S+)\s*\n"
        r"^Up Time\(HH:MM:SS\)\s+: .+\n"
        r"^HwVersion\s+:(?P<hardware>.*)\n"
        r"(^CPLDVersion\s+: .+\n)?"
        r"^CPSwVersion\s+: .+\n"
        r"^CPSwVersion\(Build\): (?P<version>\S+).*\n"
        r"^DPSwVersion\s+: .+\n",
        re.MULTILINE,
    )
    rx_ver2 = re.compile(
        r"^Object-id\s+: (?P<sys_oid>\S+)\s*\n"
        r"^Up Time\(HH:MM:SS\)\s+: .+\n"
        r"^HwVersion\s+:(?P<hardware>.*)\n"
        r"^CPSwVersion\s+: (?P<version>\S+)\s*\n"
        r"^DPSwVersion\s+: .+",
        re.MULTILINE,
    )
    rx_port = re.compile(r"Num of Ports\s+:\s*(?P<port_num>\d+)")
    OID_TABLE = {
        "1.3.6.1.4.1.171.10.65.1": "DAS-32xx",
        "1.3.6.1.4.1.3278.1.12": "DAS-3248",
        "1.3.6.1.4.1.3646.1300.6": "DAS-4192DC",
        "1.3.6.1.4.1.3646.1300.11": "DAS-3248DC",
        "1.3.6.1.4.1.3646.1300.12": "DAS-3248",
        "1.3.6.1.4.1.3646.1300.13": "DAS-3224DC",
        "1.3.6.1.4.1.3646.1300.14": "DAS-3224",
        "1.3.6.1.4.1.3646.1300.15": "DAS-3216DC",
        "1.3.6.1.4.1.3646.1300.16": "DAS-3216",
        "1.3.6.1.4.1.3646.1300.19": "DAS-3248/E",
        "1.3.6.1.4.1.3646.1300.202": "DAS-3224/E",
    }

    def execute_snmp(self, **kwargs):
        vendor = "DLink"
        p = self.snmp.get(mib["SNMPv2-MIB::sysObjectID", 0])
        platform = self.OID_TABLE[p]
        if platform == "DAS-32xx":
            # Conexant
            version = self.snmp.get("1.3.6.1.4.1.171.10.65.1.6.1.3.0")
        else:
            version = self.snmp.get("")
        if platform.startswith("DAS-41"):
            # For DAS-4192DC
            version = self.snmp.get("1.3.6.1.4.1.3646.1300.6.1.11.1.4.10500")
        if p == "1.3.6.1.4.1.3278.1.12":
            n = self.snmp.get("1.3.6.1.2.1.1.5.0")
            if n.startswith("FG-ACE-24"):
                vendor = "Nateks"
                platform = "FG-ACE-24"
        return {"vendor": vendor, "platform": platform, "version": version}

    def get_conexant_platform(self):
        v = self.cli("get system manuf info", cached=True)
        port_num = self.rx_port.search(v).group("port_num")
        return "DAS-3224" if int(port_num) == 24 else "DAS-3248"

    def get_vendor(self, v: str) -> Tuple[str, str]:
        """
        Normalize platform name for DAS- models
        :param platform:
        :return:
        """
        match1 = self.rx_vendor.search(v)
        if match1 and match1.group("vendor").startswith("FG-ACE-24"):
            return (
                "Nateks",
                "FG-ACE-24",
            )
        platform = self.OID_TABLE[match.group("sys_oid")]
        if platform == "DAS-32xx":
            platform = self.get_conexant_platform()
        return "DLink", platform
        return "DLink", None

    def execute_cli(self, **kwargs):
        v = self.cli("get system info")
        vendor = "DLink"
        match = self.rx_descr.search(v)
        platform = match.group("platform")
        if not platform:
            raise NotImplementedError
        # Version
        match = self.rx_ver.search(v)
        if not match:
            match = self.rx_ver2.search(v)
        # Fix vendor
        if not platform.startswith("DAS-"):
            match1 = self.rx_vendor.search(v)
            if match1 and match1.group("vendor").startswith("FG-ACE-24"):
                vendor, platform = "Nateks", "FG-ACE-24"
            else:
                platform = self.OID_TABLE[match.group("sys_oid")]
                if platform == "DAS-32xx":
                    platform = self.get_conexant_platform()
        r = {
            "vendor": vendor,
            "platform": platform,
            "version": match.group("version"),
            "attributes": {},
        }
        serial, hardware = None, None
        try:
            v = self.cli("get sys eeprom256")
            r["attributes"] = {
                "Serial Number": self.rx_serial.search(v).group("serial"),
                "HW version": self.rx_hardware.search(v).group("hardware"),
            }
        except self.CLISyntaxError:
            pass
        if "HW version" not in r["attributes"] and match.group("hardware").strip():
            r["attributes"]["HW version"] = match.group("hardware").strip()
        return r
