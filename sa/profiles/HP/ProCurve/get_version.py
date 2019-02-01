# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.ProCurve.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "HP.ProCurve.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^(?:HP|ProCurve)\s+(?P<platform>\S+)\s+Switch\s+\d\S+,"
        r"\s+revision\s+(?P<version>\S+),\s+ROM\s+(?P<bootprom>\S+)", re.MULTILINE)
    rx_ver1 = re.compile(
        r"^ProCurve\s+\S+\s+(Switch\s+)?(?P<platform>\S+).*?,"
        r"\s*revision\s+(?P<version>\S+),", re.MULTILINE)
    rx_ver_new = re.compile(
        r"^HP\s+(?:\S+\s+)?(?P<platform>\S+)\s+Switch(?: Stack)?,"
        r"\s+revision\s+(?P<version>\S+),", re.MULTILINE)
    # Added for 3500yl
    rx_ver_3500yl = re.compile(
        r"^HP\s+\S+\s+(Switch\s+)?(?P<platform>\S+).*?,"
        r"\s*revision\s+(?P<version>\S+),", re.MULTILINE)

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
        match = self.rx_ver.search(v)
        if not match:
            match = self.rx_ver1.search(v)
            if not match:
                match = self.rx_ver_new.search(v)
                if not match:
                    match = self.rx_ver_3500yl.search(v)
        platform = match.group("platform").split('-')[0]
        return {
            "vendor": "HP",
            "platform": platform,
            "version": match.group("version")
        }

    def execute_cli(self):
        v = self.cli("walkMIB sysDescr", cached=True).replace("sysDescr.0 = ", "")
        match = self.rx_ver.search(v)
        if not match:
            match = self.rx_ver1.search(v)
            if not match:
                match = self.rx_ver_new.search(v)
                if not match:
                    match = self.rx_ver_3500yl.search(v)
        platform = match.group("platform").split('-')[0]
        return {
            "vendor": "HP",
            "platform": platform,
            "version": match.group("version")
        }
