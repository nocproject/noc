# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
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

    rx_version = re.compile(
        r"^(?:Cisco IOS Software( \[Everest\])?,.*?|IOS \(tm\)) (IOS[\-\s]XE Software,\s)?"
        r"(?P<platform>.+?) Software \((?P<image>[^)]+)\), (Experimental )?"
        r"Version (?P<version>[^\s,]+)", re.MULTILINE | re.DOTALL)
    rx_snmp_ver = re.compile(
        r"^(?:Cisco IOS Software( \[Everest\])?,.*?|IOS \(tm\)) (?P<platform>.+?) Software "
        r"\((?P<image>[^)]+)\), (Experimental )?Version (?P<version>[^,]+),",
        re.MULTILINE | re.DOTALL)
    rx_platform = re.compile(
        r"^cisco (?P<platform>\S+) \(\S+\) processor( \(revision.+?\))? with",
        re.IGNORECASE | re.MULTILINE)
    rx_invalid_platforms = re.compile(
        r"IOS[\-\s]XE|EGR|Catalyst( \S+)? L3 Switch|s\d+\S+")
    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\", DESCR: \"(?P<descr>[^\"]+)\"\n"
        r"PID:\s+(?P<pid>\S+)?\s*,\s+VID:\s+(?P<vid>\S+)?\s*, "
        r"SN:\s(?P<serial>\S+)?", re.MULTILINE | re.DOTALL)
    rx_7100 = re.compile(
        r"^(?:uBR|CISCO)?71(?:20|40|11|14)(-\S+)? "
        r"(?:Universal Broadband Router|chassis)")
    rx_ver = re.compile(
        r"Model revision number\s+:\s+(?P<revision>\S+)\s*\n"
        r"Motherboard revision number\s+:\s+\S+\s*\n"
        r"Model number\s+:\s+(?P<part_no>\S+)\s*\n"
        r"System serial number\s+:\s+(?P<serial>\S+)\s*\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)
    rx_ver1 = re.compile(
        r"^cisco (?P<part_no>\S+) \(\S+\) processor( "
        r"\(revision(?P<revision>.+?)\))? with",
        re.IGNORECASE | re.MULTILINE)
    IGNORED_SERIAL = set([
        "H22L714"
    ])
    IGNORED_NAMES = set([
        "c7201"
    ])

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

    def execute(self):
        if self.has_snmp():
            # Try to find other varians, like this
            # https://wiki.opennms.org/wiki/Hardware_Inventory_Entity_MIB
            platform = ""
            try:
                v = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
                if v:
                    s = ""
                    match = self.rx_snmp_ver.search(v)
                    platform = match.group("platform")
                    # inventory
                    # p = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.2.1001")
                    p = self.snmp.get(mib["ENTITY-MIB::entPhysicalDescr.1001"])
                    if p and p.startswith("WS-C"):
                        platform = p
                        s = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum.1001"])
                    else:
                        # Found in WS-C3650-48TD
                        p = self.snmp.get(mib["ENTITY-MIB::entPhysicalDescr.1000"])
                        if p and p.startswith("WS-C"):
                            platform = p
                            s = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum.1000"])
                        else:
                            # CISCO-ENTITY-MIB::entPhysicalModelName
                            p = self.snmp.get(mib["ENTITY-MIB::entPhysicalModelName.1"])
                            # WS-C4500X-32 return '  '
                            if p is None or p.strip() == "":
                                # Found in WS-C4500X-32
                                p = self.snmp.get(mib["ENTITY-MIB::entPhysicalModelName.1000"])
                            if p:
                                if p.startswith("CISCO"):
                                    p = p[5:]
                                if p.endswith("-CHASSIS"):
                                    p = p[:-8]
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
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
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
                    (
                        i == 0 or pid.startswith("CISCO") or
                        pid.startswith("WS-C")
                    ) and
                    not pid.startswith("WS-CAC-") and
                    not pid.endswith("-MB") and
                    "Clock" not in descr and "VTT FRU" not in descr and
                    "C2801 Motherboard " not in descr
                ):
                    if pid in ("", "N/A"):
                        if self.rx_7100.search(descr):
                            pid = "CISCO7100"
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
