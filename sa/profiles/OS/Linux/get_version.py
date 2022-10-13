# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OS.Linux.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "OS.Linux.get_version"
    cache = True
    interface = IGetVersion

    ver_map = {
        "name": "distr",
        "pretty_name": "full_name",
        "version": "version",
        "version_id": "version_id",
        "version_codename": "codename"
    }

    def execute_cli(self):
        version = None
        codename = ""
        distr = ""

        r = self.cli("cat /etc/os-release", cached=True)
        if "No such file or directory" not in r:
            res = parse_kv(self.ver_map, r, sep="=")
            distr = res["distr"].replace("\"", "")
            version = res["version"].replace("\"", "")
            name = res["full_name"].replace("\"", "")
            if "codename" in res:
                codename = res["codename"].replace("\"", "")
        bit = self.cli("uname -m").strip()
        kernel = self.cli("uname -r").strip()

        return {
            "vendor": distr,
            "platform": name,
            "version": version,
            "attributes": {
                "codename": codename,
                "architecture": bit,
                "kernel": kernel.strip(),
            },
        }
