# ---------------------------------------------------------------------
# EdgeCore.ES.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "EdgeCore.ES.get_version"
    cache = True
    interface = IGetVersion

    def execute_snmp(self):
        s = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
        oid = self.snmp.get(mib["SNMPv2-MIB::sysObjectID.0"], cached=True)
        if oid == "":
            raise self.snmp.TimeOutError  # Fallback to CLI
        if ", " in oid:
            oid = oid[1:-1].replace(", ", ".")
        if oid[-3:] == "2.4":
            # 3528M-SFP OID (v1.4.x.x)
            v = self.snmp.get(oid[:-3] + "1.4.1.1.3.1.6.1", cached=True)
        elif oid[-3:] == "101":
            # 3528MV2-Style OID
            v = self.snmp.get(oid[:-3] + "1.1.3.1.6.1", cached=True)
        else:
            # 3526-Style OID
            v = self.snmp.get(oid + ".1.1.3.1.6.1", cached=True)
        if v == "":
            # 4626-Style OID
            v = self.snmp.get(oid + ".100.1.3.0", cached=True)
            if v == "":
                raise self.snmp.TimeOutError  # Fallback to CLI
        if self.rx_sys_4.search(s):
            return self.get_version_4xxx(s, v)
        return self.get_version_35xx("System description : " + s, v)

    #
    # Main dispatcher
    #
    def execute_cli(self):
        try:
            s = self.cli("show system", cached=True)
        except self.CLISyntaxError:
            # Get 4xxx version
            return self.get_version_4xxx(None, None)
        return self.get_version_35xx(s, None)

    #
    # 35xx
    #
    rx_sys_35 = re.compile(r"^\s*System [Dd]escription\s*:\s(?P<platform>.+?)\s*$", re.MULTILINE)
    rx_sys_42 = re.compile(r"^\s*System OID String\s*:\s(?P<platform>.+?)\s*$", re.MULTILINE)
    rx_ver_35 = re.compile(
        r"^\s*Operation [Cc]ode [Vv]ersion\s*:\s*(?P<version>\S+)\s*$", re.MULTILINE
    )
    rx_ser_35 = re.compile(r"^\s*Serial Number\s*:\s*(?P<serial>\S+)\s*$", re.MULTILINE)
    rx_hw_35 = re.compile(r"^\s*Hardware Version\s*:\s*(?P<hardware>\S+)\s*$", re.MULTILINE)
    rx_boot_35 = re.compile(r"^\s*Boot ROM Version\s+:\s+(?P<boot>.+)\s*$", re.MULTILINE)

    PLATFORM_TYPES = {
        "1.3.6.1.4.1.259.10.1.42.101": "ECS4210-28T",
        "1.3.6.1.4.1.259.10.1.42.102": "ECS4210-28P",
        "1.3.6.1.4.1.259.10.1.42.103": "ECS4210-12T",
        "1.3.6.1.4.1.259.10.1.42.104": "ECS4210-12P",
        "1.3.6.1.4.1.259.10.1.24.101": "ECS4510-28T",
        "1.3.6.1.4.1.259.10.1.24.102": "ECS4510-28P",
        "1.3.6.1.4.1.259.10.1.24.103": "ECS4510-28F",
        "1.3.6.1.4.1.259.10.1.24.104": "ECS4510-52T",
        "1.3.6.1.4.1.259.10.1.10": "ECS4660-28F",
        "1.3.6.1.4.1.259.6.10.50": "ES3526X",
    }

    def get_version_35xx(self, show_system, version):
        # Vendor default
        vendor = "EdgeCore"
        # Detect version
        if not version:
            v = self.cli("show version", cached=True)
            match = self.re_search(self.rx_ver_35, v)
            version = match.group("version")
        else:
            v = ""
        # Detect platform
        match = self.rx_sys_35.search(show_system)
        platform = match.group("platform")
        if "ES3526XA" in platform:
            # Detect ES3626XA hardware version
            sub = version.split(".")
            if sub[0] == "1":
                platform = "ES3526XA-V2"
            elif sub[0] == "2" and sub[1] == "3":
                if int(sub[2]) & 1 == 1:
                    platform = "ES3526XA-38"
                else:
                    platform = "ES3526XA-1-SL-38"
            else:
                raise self.NotSupportedError(platform)
        elif "3510MA" in platform:
            platform = "ES3510MA"
        elif "ECS3510-" in platform:
            pass
        elif "3510" in platform:
            platform = "ES3510"
        elif "3552M" in platform:
            platform = "ES3552M"
        elif "ES3528M" in platform:
            platform = "ES3528M"
        elif "ES3526S" in platform:
            pass
        elif "ECS4100-28T" in platform:
            pass
        elif "ECS4100-52T" in platform:
            pass
        elif "MR2228N" in platform:
            vendor = "MRV"
        elif (
            platform.lower() == "8 sfp ports + 4 gigabit combo ports "
            "l2/l3/l4 managed standalone switch"
        ):
            platform = "ES4612"
        elif platform == "Managed 8G+4GSFP Switch":
            platform = "ECS4210-12T"
        elif platform == "Managed 24G+4GSFP Switch":
            platform = "ECS4210-28T"
        else:
            match = self.rx_sys_42.search(show_system)
            if not match:
                raise self.NotSupportedError(platform)
            platform = self.PLATFORM_TYPES.get(match.group("platform"))
            if not platform:
                raise self.NotSupportedError(match.group("platform"))
        r = {"vendor": vendor, "platform": platform, "version": version, "attributes": {}}
        if not v:
            return r
        match = self.rx_boot_35.search(v)
        if match:
            r["attributes"].update({"Boot PROM": match.group("boot")})
        match = self.rx_hw_35.search(v)
        if match:
            r["attributes"].update({"HW version": match.group("hardware")})
        match = self.rx_ser_35.search(v)
        if match:
            r["attributes"].update({"Serial Number": match.group("serial")})
        return r

    #
    # ES4626
    #
    rx_sys_4 = re.compile(r"(?P<platform>ES.+?|Switch) Device, Compiled")
    rx_ver_4 = re.compile(
        r"SoftWare (Package )?Version.*?(?:_|Vco\.| )(?P<version>\d.+?)$", re.MULTILINE
    )
    rx_boot_4 = re.compile(r"BootRom Version (\S+_)?(?P<boot>\d.+?)$", re.MULTILINE)
    rx_hw_4 = re.compile(r"HardWare Version (\S+_)?(?P<hardware>\S+)$", re.MULTILINE)
    rx_ser_4 = re.compile(r"Device serial number (\S+_)?(?P<serial>\S+)$", re.MULTILINE)

    def get_version_4xxx(self, v, version):
        if not v:
            v = self.cli("show version 1", cached=True)
        match_sys = self.re_search(self.rx_sys_4, v)
        platform = match_sys.group("platform")
        if platform == "Switch":
            platform = "Unknown"
        if not version:
            match_ver = self.re_search(self.rx_ver_4, v)
            version = match_ver.group("version")
        r = {"vendor": "EdgeCore", "platform": platform, "version": version, "attributes": {}}
        match = self.rx_boot_4.search(v)
        if match:
            r["attributes"].update({"Boot PROM": match.group("boot")})
        match = self.rx_hw_4.search(v)
        if match:
            r["attributes"].update({"HW version": match.group("hardware")})
        match = self.rx_ser_4.search(v)
        if match:
            r["attributes"].update({"Serial Number": match.group("serial")})
        return r
