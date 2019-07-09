# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_version"
    cache = True
    interface = IGetVersion

    # Some versions of Mikrotik return parameter values in quotes
    rx_ver = re.compile(r"^\s+version: (?P<q>\"?)(?P<version>.*)(?P=q)\s*\n", re.MULTILINE)
    rx_arch = re.compile(r"^\s+architecture-name: (?P<q>\"?)(?P<arch>.*)(?P=q)\s*\n", re.MULTILINE)
    rx_platform = re.compile(r"^\s+board-name: (?P<q>\"?)(?P<platform>.*)(?P=q)\s*\n", re.MULTILINE)
    rx_serial = re.compile(
        r"^\s+serial-number: (?P<q>\"?)(?P<serial>\S+?)(?P=q)\s*\n", re.MULTILINE
    )
    rx_boot = re.compile(r"^\s+current-firmware: (?P<q>\"?)(?P<boot>\S+?)(?P=q)\s*\n", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("/system resource print")
        version = self.rx_ver.search(v).group("version")
        if " " in version:
            version = version.split(" ", 1)[0]
        platform = self.rx_platform.search(v).group("platform")
        match = self.rx_arch.search(v)
        if match:
            arch = match.group("arch")
            # platform = "%s (%s)" % (platform, arch)
        else:
            arch = None
        r = {"vendor": "MikroTik", "platform": platform, "version": version, "attributes": {}}
        if "x86" not in platform and "CHR" not in platform:
            v = self.cli("/system routerboard print")
            match = self.rx_serial.search(v)
            if match:
                r["attributes"]["Serial Number"] = match.group("serial")
            match = self.rx_boot.search(v)
            if match:
                r["attributes"]["Boot PROM"] = match.group("boot")
            if arch:
                r["attributes"]["Arch"] = arch
        return r
