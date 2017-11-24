# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
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

    rx_ver = re.compile(
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
        r"IOS[\-\s]XE|EGR|Catalyst L3 Switch|s\d+\S+")

    def execute(self):
        if self.has_snmp():
            # Try to find other varians, like this
            # https://wiki.opennms.org/wiki/Hardware_Inventory_Entity_MIB
            platform = ""
            try:
                v = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
                if v:
                    s = ""
                    match = self.re_search(self.rx_snmp_ver, v)
                    platform = match.group("platform")
                    # inventory
                    p = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.2.1001")
                    if p and p.startswith("WS-C"):
                        platform = p
                        s = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.1001")
                    else:
                        # Found in WS-C3650-48TD
                        p = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.2.1000")
                        if p and p.startswith("WS-C"):
                            platform = p
                            s = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.1000")
                        else:
                            # CISCO-ENTITY-MIB::entPhysicalModelName
                            p = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.13.1")
                            if p:
                                if p.startswith("CISCO"):
                                    p = p[5:]
                                if p.endswith("-CHASSIS"):
                                    p = p[:-8]
                                platform = p
                    if not self.rx_invalid_platforms.search(platform):
                        r = {
                            "vendor": "Cisco",
                            "platform": platform,
                            "version": match.group("version"),
                            "image": match.group("image"),
                        }
                        if s:
                            r["attributes"] = {}
                            r["attributes"]["Serial Number"] = s
                        return r
            except self.snmp.TimeOutError:
                pass
        serial = None
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        for i in self.scripts.get_inventory():
            if i["type"] == "CHASSIS":
                serial = i.get("serial")
                r = {
                    "vendor": "Cisco",
                    "platform": i["part_no"],
                    "version": match.group("version"),
                    "image": match.group("image"),
                }
                break
        if serial:
            r["attributes"] = {}
            r["attributes"]["Serial Number"] = serial
        return r
