# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC Modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "EdgeCore.ES.get_version"
    cache = True
    implements = [IGetVersion]

    ##
    ## Main dispatcher
    ##
    def execute(self):
        s = ""
        if self.snmp and self.access_profile.snmp_ro:
            # Trying SNMP
            try:
                # SNMPv2-MIB::sysDescr.0
                s = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                # SNMPv2-MIB::sysObjectID.0
                oid = self.snmp.get("1.3.6.1.2.1.1.2.0", cached=True)
                if oid == "":
                    raise self.snmp.TimeOutError  # Fallback to CLI
                if ", " in oid:
                    oid = oid[1: -1].replace(", ", ".")
                if oid[-3:] == "2.4":
                    # 3528M-SFP OID (v1.4.x.x)
                    v = self.snmp.get(oid[: -3] + "1.4.1.1.3.1.6.1",
                        cached=True)
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
            except self.snmp.TimeOutError:
                pass
        if s == "":
            # Trying CLI
            try:
                s = self.cli("show system", cached=True)
            except self.CLISyntaxError:
                # Get 4xxx version
                return self.get_version_4xxx(None, None)
            return self.get_version_35xx(s, None)

    ##
    ## 35xx
    ##
    rx_sys_35 = re.compile(
        r"^\s*System description\s*:\s(?P<platform>.+?)\s*$",
        re.MULTILINE | re.IGNORECASE)
    rx_ver_35 = re.compile(
        r"^\s*Operation code version\s*:\s*(?P<version>\S+)\s*$",
        re.MULTILINE | re.IGNORECASE)
    rx_ser_35 = re.compile(
        r"^\s*Serial Number\s*:\s*(?P<serial>\S+)\s*$",
        re.MULTILINE | re.IGNORECASE)
    rx_hw_35 = re.compile(
        r"^\s*Hardware Version\s*:\s*(?P<hardware>\S+)\s*$",
        re.MULTILINE | re.IGNORECASE)
    rx_boot_35 = re.compile(
        r"^\s*Boot ROM Version\s+:\s+(?P<boot>.+)\s*$",
        re.MULTILINE | re.IGNORECASE)

    def get_version_35xx(self, show_system, version):
        # Vendor default
        vendor = "EdgeCore"
        # Detect version
        if not version:
            v = self.cli("show version", cached=True)
            match = self.re_search(self.rx_ver_35, v)
            version = match.group("version")
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
        elif "3510" in platform:
            platform = "ES3510"
        elif "3552M" in platform:
            platform = "ES3552M"
        elif "ES3528M" in platform:
            platform = "ES3528M"
        elif "ES3526S" in platform:
            pass
        elif "MR2228N" in platform:
            vendor = "MRV"
        elif platform.lower() == "8 sfp ports + 4 gigabit combo ports l2/l3/l4 managed standalone switch":
            platform = "ES4612"
        elif platform == "Managed 8G+4GSFP Switch":
            platform = "ECS4210-12T"
        elif platform == "Managed 24G+4GSFP Switch":
            platform = "ECS4210-28T"
        else:
            raise self.NotSupportedError(platform)
        r = {
            "vendor": vendor,
            "platform": platform,
            "version": version,
            "attributes": {}
        }
        v = self.cli("show version", cached=True)
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

    ##
    ## ES4626
    ##
    rx_sys_4 = re.compile(r"(?P<platform>ES.+?) Device, Compiled",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_ver_4 = re.compile(
        r"SoftWare (Package )?Version.*?(?:_|Vco\.)(?P<version>\d.+?)$",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_boot_4 = re.compile(
        r"BootRom Version (\S+_)?(?P<boot>\d.+?)$",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_hw_4 = re.compile(
        r"HardWare Version (\S+_)?(?P<hardware>\S+)$",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_ser_4 = re.compile(
        r"Device serial number (\S+_)?(?P<serial>\S+)$",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def get_version_4xxx(self, v, version):
        if not v:
            v = self.cli("show version 1", cached=True)
        match_sys = self.re_search(self.rx_sys_4, v)
        if not version:
            match_ver = self.re_search(self.rx_ver_4, v)
            version = match_ver.group("version")
        r = {
            "vendor": "EdgeCore",
            "platform": match_sys.group("platform"),
            "version": version,
            "attributes": {}
        }
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

