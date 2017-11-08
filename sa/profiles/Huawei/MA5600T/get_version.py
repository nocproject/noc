# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Huawei.MA5600T.get_version"
    cache = True
    interface = IGetVersion

    rx_ver1 = re.compile(
        r"^\s*(?P<platform>[UM]A\S+)(?P<version>V\d+R\d+\S*)\s*.+\n"
        r"(^\s*PRODUCT (?P<platform1>MA\S+)\s*\n)?",
        re.MULTILINE)
    rx_ver2 = re.compile(
        r"^\s*VERSION\s*:\s*MA\S+(?P<version>V\d+R\d+\S+)\s*\n"
        r".+?"
        r"^\s*PRODUCT\s+(\:\s*)?(?P<platform>MA\S+)\s*\n",
        re.MULTILINE | re.DOTALL)
    rx_ver3 = re.compile(
        r"^\s*VERSION\s*:\s*(?P<platform>(MA|UA)\S+)(?P<version>V\d+R\d+\S+)\s*\n",
        re.MULTILINE)

    def execute(self):
        v = self.cli("display version\n")
        match = self.rx_ver1.search(v)
        if match:
            platform = match.group("platform")
            platform1 = match.group("platform1")
            if platform1 and platform1 != platform:
                platform = platform1
            return {
                "vendor": "Huawei",
                "platform": platform,
                "version": match.group("version")
            }
        else:
            match = self.rx_ver2.search(v)
            if match:
                return {
                    "vendor": "Huawei",
                    "platform": match.group("platform"),
                    "version": match.group("version")
                }
            else:
                match = self.rx_ver3.search(v)
                return {
                    "vendor": "Huawei",
                    "platform": match.group("platform"),
                    "version": match.group("version")
                }
