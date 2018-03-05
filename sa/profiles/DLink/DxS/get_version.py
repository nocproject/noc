# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.sa.profiles.DLink.DxS import get_platform
from noc.core.mib import mib


class Script(BaseScript):
    name = "DLink.DxS.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(
        r"Device Type\s+:\s*(?P<platform>\S+).+"
        r"(?:Boot PROM|System [Bb]oot)\s+"
        r"[Vv]ersion\s+:\s*(?:Build\s+)?(?P<bootprom>\S+).+"
        r"[Ff]irmware [Vv]ersion(?: 1)?\s+:\s*(?:Build\s+)?(?P<version>\S+).+"
        r"[Hh]ardware [Vv]ersion\s+:\s*(?P<hardware>\S+)",
        re.MULTILINE | re.DOTALL)
    rx_fwt = re.compile(
        r"(?:Firmware Type|System [Ff]irmware [Vv]ersion)\s+:\s*"
        r"(?P<fwt>\S+)\s*\n", re.MULTILINE | re.DOTALL)
    rx_ser = re.compile(
        r"(?:[Ss]erial [Nn]umber|Device S/N)\s+:\s*(?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL)
    rx_platform = re.compile("^(?:D-Link )?(?P<platform>\S+)\s+")

    def execute_snmp(self):
        """
        AGENT-MIB and AGENT-GENERAL-MIB - D-Link private MIBs
        """
        platform = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.7.1", cached=True)
        hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.1", cached=True)
        version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.1", cached=True)
        bootprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.1", cached=True)
        serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.1", cached=True)
        # Found in some devices
        if str(bootprom) == str(version):
            bootprom = ""
        if not serial:
            # AGENT-GENERAL-MIB::agentSerialNumber
            serial = self.snmp.get("1.3.6.1.4.1.171.12.1.1.12.0", cached=True)
        # AGENT-GENERAL-MIB::agentFirmwareType
        fwt = self.snmp.get("1.3.6.1.4.1.171.12.1.1.13.0", cached=True)

        if not platform or not version:
            v = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
            match = self.rx_platform.search(v)
            platform = match.group("platform")
            # RMON2-MIB::probeSoftwareRev
            version = self.snmp.get("1.3.6.1.2.1.16.19.2", cached=True)
            if not version:
                version = self.snmp.get("1.3.6.1.2.1.16.19.2.0", cached=True)
            # RMON2-MIB::probeHardwareRev
            hardware = self.snmp.get("1.3.6.1.2.1.16.19.3", cached=True)
            if not hardware:
                hardware = self.snmp.get("1.3.6.1.2.1.16.19.3.0", cached=True)
        if not version:
            # AGENT-MIB::swMultiImageInfoEntry
            info_entry = "1.3.6.1.4.1.171.12.1.2.7.1"
            image_id = 0
            for oid, v in self.snmp.getnext(info_entry, max_repetitions=10):
                # AGENT-MIB::swMultiImageInfoID
                if oid.startswith("%s.1" % info_entry):
                    image_id = int(v)
                # AGENT-MIB::swMultiImageVersion
                if oid.startswith("%s.2.%s" % (info_entry, image_id)):
                    version = v
                    if version.startswith("Build "):
                        version = version[6:]
                    break
        r = {
            "vendor": "DLink",
            "platform": get_platform(
                platform, hardware
            ),
            "version": version,
            "attributes": {}
        }
        if bootprom:
            r["attributes"]["Boot PROM"] = bootprom
        if hardware:
            r["attributes"]["HW version"] = hardware
        if serial:
            r["attributes"]["Serial Number"] = serial
        if fwt and fwt != version:
            r["attributes"]["Firmware Type"] = fwt
        return r

    def execute_cli(self):
        s = self.scripts.get_switch()
        match = self.rx_ver.search(s)
        r = {
            "vendor": "DLink",
            "platform": get_platform(
                match.group("platform"), match.group("hardware")
            ),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
            }
        }
        ser = self.rx_ser.search(s)
        if ser and ser.group("serial") not in ["System", "Power"]:
            r["attributes"]["Serial Number"] = ser.group("serial")
        fwt = self.rx_fwt.search(s)
        if fwt and fwt.group("fwt") != match.group("version"):
            r["attributes"]["Firmware Type"] = fwt.group("fwt")
        return r
