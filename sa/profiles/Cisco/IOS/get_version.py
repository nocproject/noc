# ---------------------------------------------------------------------
# Cisco.IOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Cisco.IOS.get_version"
    cache = True
    interface = IGetVersion
    always_prefer = "S"

    rx_version = re.compile(
        r"^(?:Cisco IOS Software( \[(?:Gibraltar|Fuji|Everest|Denali|Amsterdam|Bengaluru)\])?,.*?|IOS \(tm\)) (IOS[\-\s]XE "
        r"Software,\s)?(?P<platform>.+?) Software \((?P<image>[^)]+)\), (Experimental )?"
        r"Version (?P<version>[^\s,]+)",
        re.MULTILINE | re.DOTALL,
    )
    rx_snmp_ver = re.compile(
        r"^(?:Cisco IOS Software( \[(?:Gibraltar|Fuji|Everest|Denali|Amsterdam|Bengaluru)\])?,.*?|IOS \(tm\)) (?P<platform>.+?) "
        r"Software \((?P<image>[^)]+)\), (Experimental )?Version (?P<version>[^\s,]+)",
        re.MULTILINE | re.DOTALL,
    )
    rx_platform = re.compile(
        r"^cisco (?P<platform>\S+) \(\S+\) processor( \(revision.+?\))? with",
        re.IGNORECASE | re.MULTILINE,
    )
    rx_old_platform = re.compile(r"^(?P<platform>\S+) chassis")
    rx_invalid_platforms = re.compile(r"IOS[\-\s]XE|EGR|Catalyst( \S+)? L3 Switch|s\d+\S+")
    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\", DESCR: \"(?P<descr>[^\"]+)\"\n"
        r"PID:\s+(?P<pid>\S+)?\s*,\s+VID:\s+(?P<vid>\S+)?\s*, "
        r"SN:\s(?P<serial>\S+)?",
        re.MULTILINE | re.DOTALL,
    )
    rx_7100 = re.compile(
        r"^(?:uBR|CISCO)?71(?:20|40|11|14)(-\S+)? " r"(?:Universal Broadband Router|chassis)"
    )
    rx_c4900m = re.compile(r"^Cisco Systems, Inc. (?P<part_no>\S+) \d+ slot switch")
    rx_ver = re.compile(
        r"Model revision number\s+:\s+(?P<revision>\S+)\s*\n"
        r"Motherboard revision number\s+:\s+\S+\s*\n"
        r"Model number\s+:\s+(?P<part_no>\S+)\s*\n"
        r"System serial number\s+:\s+(?P<serial>\S+)\s*\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    rx_ver1 = re.compile(
        r"^cisco (?P<part_no>\S+) \(\S+\) processor( " r"\(revision(?P<revision>.+?)\))? with",
        re.IGNORECASE | re.MULTILINE,
    )
    IGNORED_SERIAL = {"H22L714"}
    IGNORED_NAMES = {"c7201"}

    def clear_platform(self, platform):
        """
        Clear platform string
        :param platform:
        :return:
        """
        # Clear K9 in platform
        if platform.endswith("/K9"):
            platform = platform[:-3]

        return platform

    def execute_snmp(self, **kwargs):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
        if v:
            s = ""
            match = self.rx_snmp_ver.search(v)
            platform = match.group("platform")
            # inventory
            # p = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.2.1001")
            p = self.snmp.get(mib["ENTITY-MIB::entPhysicalDescr", 1001])
            if p and (p.startswith("WS-C") or p.startswith("ME-3") or p.startswith("C6800")):
                platform = p
                s = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum", 1001])
            else:
                # Found in WS-C3650-48TD
                p = self.snmp.get(mib["ENTITY-MIB::entPhysicalDescr", 1000])
                if p and p.startswith("WS-C"):
                    platform = p
                    s = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum", 1000])
                else:
                    # CISCO-ENTITY-MIB::entPhysicalModelName
                    p = self.snmp.get(mib["ENTITY-MIB::entPhysicalModelName", 1])
                    if not p:
                        # Found in WS-C650X-E
                        p = self.snmp.get(mib["ENTITY-MIB::entPhysicalModelName", 2])
                        s = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum", 2])
                    # WS-C4500X-32 return '  ', WS-C4900M return 'MIDPLANE'
                    if p is None or p.strip() in ["", "MIDPLANE"]:
                        # Found in WS-C4500X-32 and WS-C4900M
                        p = self.snmp.get(mib["ENTITY-MIB::entPhysicalModelName", 1000])
                        s = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum", 1000])
                        if p is None:
                            # Found on C2600 series
                            p = self.snmp.get(mib["ENTITY-MIB::entPhysicalDescr", 1])
                            s = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum", 1])
                    elif not s:
                        s = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum", 1])
                    if p in ["Catalyst 37xx Switch Stack", "Catalyst C29xx Switch Stack"]:
                        # Found on 37xx and C29xx
                        p = self.snmp.get(mib["ENTITY-MIB::entPhysicalDescr", 2001])
                        s = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum", 2001])
                    if p:
                        p = p.strip()  # Cisco 3845 return 'CISCO3845         '
                        if p.startswith("CISCO"):
                            p = p[5:]
                        if p.endswith("-CHASSIS"):
                            p = p[:-8]
                        # '2651XM chassis, Hw Serial#: 2297211811, Hw Revision: 0x301'
                        match1 = self.rx_old_platform.search(p)
                        if match1:
                            p = match1.group("platform")
                        platform = p
            version = match.group("version")
            # WS-C4500X-32 do not have ',' in version string
            n = version.find(" RELEASE SOFTWARE")
            if n > 0:
                version = version[:n]
            if not self.rx_invalid_platforms.search(platform):
                r = {
                    "vendor": "Cisco",
                    "platform": self.clear_platform(platform),
                    "version": version,
                    "image": match.group("image"),
                }
                if s:
                    r["attributes"] = {}
                    r["attributes"]["Serial Number"] = s
                return r

    def execute_cli(self, **kwargs):
        c = ""
        try:
            v = self.cli("show inventory raw")
            i = 0
            serial = None
            for match in self.rx_item.finditer(v):
                name = match.group("name")
                pid = match.group("pid")
                if pid is None:
                    pid = ""
                descr = match.group("descr")
                if name in self.IGNORED_NAMES:
                    continue
                if (
                    (i == 0 or pid.startswith("CISCO") or pid.startswith("WS-C"))
                    and not pid.startswith("WS-CAC-")
                    and not pid.endswith("-MB")
                    and "Clock" not in descr
                    and "VTT FRU" not in descr
                    and "C2801 Motherboard " not in descr
                    and "xx Switch Stack" not in descr
                ):
                    if pid in ("", "N/A"):
                        if self.rx_7100.search(descr):
                            pid = "CISCO7100"
                    if pid == "MIDPLANE" and name == "Switch System":
                        match1 = self.rx_c4900m.search(descr)
                        if match1:
                            pid = match1.group("part_no")
                    if pid.startswith("CISCO"):
                        pid = pid[5:]
                    platform = pid
                    serial = match.group("serial")
                    break
                i = 1
            if serial in self.IGNORED_SERIAL:
                serial = None
        except self.CLISyntaxError:
            c = self.cli("show version", cached=True)
            match = self.rx_ver.search(c)
            if match:
                platform = match.group("part_no")
                serial = match.group("serial")
            else:
                match = self.rx_ver1.search(c)
                if match:
                    platform = match.group("part_no")
                    serial = None
                else:
                    raise self.NotSupportedError()
        if c == "":
            c = self.cli("show version", cached=True)
        match = self.rx_version.search(c)
        if not platform:
            platform = match.group("platform")
        if self.rx_invalid_platforms.search(platform):
            # Process IOS XE platform
            match1 = self.rx_platform.search(c)
            if match1:
                platform = match1.group("platform")
        version = match.group("version")
        # WS-C4500X-32 do not have ',' in version string
        n = version.find(" RELEASE SOFTWARE")
        if n > 0:
            version = version[:n]
        r = {
            "vendor": "Cisco",
            "platform": self.clear_platform(platform),
            "version": version,
            "image": match.group("image"),
        }
        if bool(serial):
            r["attributes"] = {}
            r["attributes"]["Serial Number"] = serial
        return r
