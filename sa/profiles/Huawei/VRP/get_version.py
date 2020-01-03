# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.core.mib import mib
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "Huawei.VRP.get_version"
    cache = True
    interface = IGetVersion
    always_prefer = "S"

    rx_simple_version = re.compile(r"\d+\.\d+")

    rx_ver = re.compile(
        r"^VRP.+Software, Version (?P<version>[^ ,]+),?\s*(\(\S+\s+(?P<image>\S+)\))?.*?\n"
        r"\s*(?:Quidway|Huawei) (?P<platform>(?:NetEngine\s+|MultiserviceEngine\s+)?\S+)[^\n]+uptime",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_ver_snmp = re.compile(
        r"Versatile Routing Platform Software.*?"
        r"Version (?P<version>[^ ,]+),?\s*(\(\S+\s+(?P<image>\S+)\))?.*?\n"
        r"\s*(?:Quidway|Huawei) (?P<platform>(?:NetEngine\s+)?"
        r"[^ \t\n\r\f\v\-]+)[^\n]+",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_ver_snmp1 = re.compile(
        r"Huawei Versatile Routing Platform Software\s*"
        r"VRP \(R\) software, Version (?P<version>\d+.\d+) \((?:C[EX]\S+|ATN\S+|ATN(?: \S+){0,2}) (?P<image>\S+)\)\s*"
        r"Copyright \(C\) \d+-\d+ Huawei Technologies Co., Ltd.\s*"
        r"(?:HUAWEI\s*)?(?P<platform>(?:C[EX]\S+|ATN\S+|ATN(?: \S+){0,2}))\s*",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_ver_snmp2 = re.compile(
        r"(?P<platform>(?:\S+\s+)?(?:S\d+|AR\d+\S*)(?:[A-Z]+-[A-Z]+)?(?:\d+\S+)?)"
        r"\s+Huawei\sVersatile\sRouting\sPlatform"
        r"\sSoftware.*Version\s(?P<version>\d+\.\d+)\s"
        r"\((?:S\d+|AR\d+\S*)\s(?P<image>\S+)+\).*",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_ver_snmp3 = re.compile(
        r"^\s*VRP.+Software, Version (?P<version>\S+)\s+"
        r"\((?P<platform>S\S+|CX\d+) (?P<image>[^)]+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_ver_snmp4_ne_me = re.compile(
        r"Huawei Versatile Routing Platform Software.*?"
        r".+Version (?P<version>\S+)\s*(\(\S+\s+(?P<image>\S+)\))?.*?"
        r"\s*(?P<platform>NetEngine\s+|MultiserviceEngine\s+\S+|HUAWEI\s*NE\S+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_ver_snmp5 = re.compile(
        r"Huawei Versatile Routing Platform.*?"
        r"Version (?P<version>\S+) .*?"
        r"\s*(?:Quidway|Huawei) (?P<platform>[A-Z0-9]+)\s",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_ver_snmp6 = re.compile(
        r"Huawei Versatile Routing Platform .* \((?P<platform>[A-Z0-9]+) (?P<version>\S+)\) .*?",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_ver_snmp7_eudemon = re.compile(
        r"Huawei Versatile Routing Platform Software.*?"
        r".+Version (?P<version>\S+)\s*(\((?P<platform>\S+)\s+(?P<image>\S+)\))?.*?",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    rx_parts = re.compile(
        r"\[Slot_(?P<slot_n>\d+)\]\n"
        r"(.+\n)+\n\n"
        r"\[(?P<slot_type>(Main_Board|Port_\d+))\]\n"
        r"(.*\n){1,4}\n"
        r"\[(?P<part_name>Board\sProperties)\]\n"
        r"(?P<part_body>(.+\n)+)\n",
        re.IGNORECASE | re.MULTILINE,
    )

    rx_patch = re.compile(
        r"Patch Package Name\s*:(?P<patch_name>.+)\n"
        r"Patch Package Version\s*:(?P<patch_version>\S+)"
    )
    rx_hw_version = re.compile(r"HUAWEI\s(?P<platform>\S+)\s")
    rx_hw_extended_platform = re.compile(r"(?P<platform>\S+)[-,](CX|LS)\S+[-,].+")
    BAD_PLATFORM = ["", "Quidway S5600-HI"]
    hw_series = {"S2300", "S5300"}

    def fix_platform_name(self, platform):
        """
        Extended detect platfrom name for old releases
        :param platform:
        :return:
        """
        try:
            # v = self.snmp.get(mib["ENTITY-MIB::entPhysicalDescr", 150994945])
            r = self.snmp.getnext(
                mib["HUAWEI-ENTITY-EXTENT-MIB::hwEntityBomEnDesc"], only_first=True
            )
            if r:
                oid, r = r[0]
                r = self.rx_hw_extended_platform.search(r)
                return r.group("platform")
        except (self.snmp.TimeOutError, self.snmp.SNMPError):
            pass
        return platform

    def parse_serial(self):
        r = []
        if self.has_snmp():
            # Trying SNMP
            try:
                # SNMPv2-MIB::sysDescr.0
                for oid, x in self.snmp.getnext(mib["ENTITY-MIB::entPhysicalSerialNum"]):
                    if not x:
                        continue
                    r += [x.strip(smart_text(" \x00"))]
                if r:
                    return r
            except (self.snmp.TimeOutError, self.snmp.SNMPError):
                pass
        try:
            v = self.cli("display elabel slot 0")
        except self.CLISyntaxError:
            return []
        v = list(self.rx_parts.finditer(v))
        if v:
            v = v[0].groupdict()
            v = dict(x.split("=", 1) for x in v["part_body"].splitlines())
            if "BarCode" in v:
                r += [v["BarCode"].strip()]
        return r

    def parse_patch(self):
        r = []
        if self.has_snmp():
            # Trying SNMP
            try:
                # SNMPv2-MIB::sysDescr.0
                for oid, x in self.snmp.getnext(mib["HUAWEI-SYS-MAN-MIB::hwPatchVersion", 0]):
                    if not x:
                        continue
                    r += [x.strip(smart_text(" \x00"))]
                if r:
                    return r
            except (self.snmp.TimeOutError, self.snmp.SNMPError):
                pass
        try:
            v = self.cli("display patch-information")
        except self.CLISyntaxError:
            return []
        v = self.rx_patch.search(v)
        if v and v.group("patch_version"):
            r += [v.group("patch_version")]
        return r

    def parse_version(self, v):
        match_re_list = [
            self.rx_ver,
            self.rx_ver_snmp,
            self.rx_ver_snmp1,
            self.rx_ver_snmp2,
            self.rx_ver_snmp3,
            self.rx_ver_snmp5,
        ]
        platform = None
        if "NetEngine" in v or "MultiserviceEngine" in v or "HUAWEINE" in v or "HUAWEI NE" in v:
            # Use specified regex for this platform
            match_re_list.insert(0, self.rx_ver_snmp4_ne_me)
        elif "Eudemon" in v:
            match_re_list.insert(0, self.rx_ver_snmp7_eudemon)
        elif "Quidway S5600-HI" in v:  # Bad platform
            return "Quidway S5600-HI", None, None
        elif self.rx_hw_version.search(v):
            # For HUAWEI CX600-X2-M8 string
            platform = self.rx_hw_version.search(v).group("platform")
        try:
            rx = self.find_re(match_re_list, v)
        except self.UnexpectedResultError:
            raise NotImplementedError
        match = rx.search(v)
        image = None
        platform = platform or match.group("platform")
        # Convert NetEngine to NE
        if platform.lower().startswith("netengine"):
            n, p = platform.split(" ", 1)
            platform = "NE%s" % p.strip().upper()
        elif platform.lower().startswith("multiserviceengine"):
            n, p = platform.split(" ", 1)
            platform = "ME%s" % p.strip().upper()
        # Found in AR1220 and AR1220E
        elif platform.upper().startswith("HUAWEI"):
            n, p = platform.upper().split("HUAWEI", 1)
            platform = p.strip()
        if "image" in match.groupdict():
            image = match.group("image")
        return platform, match.group("version"), image

    def execute_snmp(self, **kwargs):
        try:
            v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
        except (self.snmp.TimeOutError, self.snmp.SNMPError):
            raise NotImplementedError()
        platform, version, image = self.parse_version(v)
        if platform in self.BAD_PLATFORM:
            platform = self.snmp.get(
                mib["ENTITY-MIB::entPhysicalModelName", 2]
            )  # "Quidway S5628F-HI"
            platform = platform.split()[-1]
            version1 = self.snmp.get(
                mib["ENTITY-MIB::entPhysicalSoftwareRev", 2]
            )  # like "5.20 Release 2102P01"
            version2 = self.snmp.get(
                mib["ENTITY-MIB::entPhysicalSoftwareRev", 7]
            )  # "V200R001B02D015SP02"
            version = "%s (%s)" % (version1.split()[0], version2)
        serial = []
        for oid, x in self.snmp.getnext(mib["ENTITY-MIB::entPhysicalSerialNum"]):
            if not x:
                continue
            serial += [x.strip(smart_text(" \x00"))]
        if platform in self.hw_series:
            # series name, fix
            platform = self.fix_platform_name(platform)
        r = {"vendor": "Huawei", "platform": platform, "version": version}
        attributes = {}
        if image:
            r["version"] = "%s (%s)" % (version, image)
            r["image"] = image
        if serial:
            attributes["Serial Number"] = serial[0]
        patch = self.parse_patch()
        if patch:
            attributes["Patch Version"] = patch[0]
        if attributes:
            r["attributes"] = attributes.copy()
        return r

    def execute_cli(self):
        v = ""
        if v in self.BAD_PLATFORM:
            # Trying CLI
            try:
                v = self.cli("display version", cached=True)
            except self.CLISyntaxError:
                raise NotImplementedError
        platform, version, image = self.parse_version(v)
        r = {"vendor": "Huawei", "platform": platform, "version": version}
        attributes = {}
        if image:
            r["version"] = "%s (%s)" % (version, image)
            r["image"] = image
        serial = self.parse_serial()
        if serial:
            attributes["Serial Number"] = serial[0]
        patch = self.parse_patch()
        if patch:
            attributes["Patch Version"] = patch[0]
        if attributes:
            r["attributes"] = attributes.copy()
        return r
