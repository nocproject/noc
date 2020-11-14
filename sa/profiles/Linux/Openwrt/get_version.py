# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linux.Openwrt.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Linux.Openwrt.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"DISTRIB_RELEASE='(?P<version>\S+)'\nDISTRIB_REVISION='(?P<codename>\S+)'\n\S+\nDISTRIB_ARCH='(?P<arch>\S+)'",
        re.MULTILINE,
    )

    def execute_cli(self):

        version = None
        codename = ""
        arch = ""

        r = self.cli("cat /etc/openwrt_release", cached=True)
        if "No such file or directory" not in r:
            match = self.rx_ver.search(r)
            arch = match.group("arch")
            version = match.group("codename")
            codename = match.group("version")

        kernel = self.cli("uname -r")

        return {
            "vendor": "OpenWRT Team",
            "platform": arch,
            "version": version,
            "attributes": {
                "codename": codename,
                "distro": "OpenWrt",
                "kernel": kernel.strip() + "",
            },
        }
