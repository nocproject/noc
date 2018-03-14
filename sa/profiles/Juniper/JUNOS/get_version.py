# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "Juniper.JUNOS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"Model:\s+(?P<platform>\S+).+JUNOS .*? \[(?P<version>[^\]]+)\]",
        re.MULTILINE | re.DOTALL)
    rx_snmp_ver = re.compile(
        r"Juniper Networks, Inc.\s+(?P<platform>\S+).+?JUNOS\s+"
        r"(?P<version>\S+[0-9])")

    def execute_snmp(self):
        v = self.snmp.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
        match = self.rx_snmp_ver.search(v)
        if match is None:
            raise self.snmp.TimeOutError()
        return {
            "vendor": "Juniper",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }

    def execute_cli(self):
        v = self.cli("show version")
        match = self.rx_ver.search(v)
        return {
            "vendor": "Juniper",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
