# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.WOP.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.WOP.get_version"
    cache = True
    interface = IGetVersion

    rx_snmp_ver = re.compile(r"Eltex\s+(?P<platform>\S+),\s*Version\s+(?P<version>\S+),")

    def execute_snmp(self, **kwargs):
        try:
            v = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
        except self.snmp.SNMPError:
            raise NotImplementedError
        match = self.rx_snmp_ver.search(v)
        if match:
            platform = match.group("platform")
            version = match.group("version")
        else:
            platform = self.snmp.get(mib["ENTITY-MIB::entPhysicalDescr", 1])
            version = self.snmp.get(mib["ENTITY-MIB::entPhysicalSoftwareRev", 1])
        sn = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum", 1])
        hwversion = self.snmp.get(mib["ENTITY-MIB::entPhysicalHardwareRev", 1])
        return {
            "vendor": "Eltex",
            "platform": platform,
            "version": version,
            "attributes": {"HW version": hwversion, "Serial Number": sn},
        }

    def execute_cli(self, **kwargs):
        c = self.cli("get system", cached=True)
        for line in c.splitlines():
            r = line.split(" ", 1)
            if r[0] == "model":
                platform = r[1].strip()
                if platform.startswith("Eltex "):
                    platform = platform.split(" ")[-1].strip()
            if r[0] == "version":
                version = r[1].strip()
            if r[0] == "serial-number":
                sn = r[1].strip()
        c = self.cli("get device-info", cached=True)
        for line in c.splitlines():
            r = line.split(" ", 1)
            if r[0] == "version-id":
                hwversion = r[1].strip()
        return {
            "vendor": "Eltex",
            "platform": platform,
            "version": version,
            "attributes": {"HW version": hwversion, "Serial Number": sn},
        }
