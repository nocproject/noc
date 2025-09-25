# ---------------------------------------------------------------------
# Meinberg.LANTIME.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Meinberg.LANTIME.get_version"
    cache = True
    interface = IGetVersion
    """
    Linux version 4.9.7 (root@ubuntu-server-3) (gcc version 4.2.4 (Ubuntu 4.2.4-1ubuntu4)) #1 SMP Fri Feb 3 11:02:06 UTC 2017
    """

    rx_ver = re.compile(
        r"\((?P<distr>[^,]+)\) \((?P<version>[^,]+)\((?P<codename>[^,]+)\)\)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    def execute(self):
        version = None
        codename = ""
        distr = ""

        r = self.cli("cat /proc/version", cached=True)
        if "No such file or directory" not in r:
            match = self.rx_ver.search(r)
            version = match.group("version")
            codename = match.group("codename")
            distr = match.group("distr")

        plat = self.cli("uname -p", cached=True)
        kernel = self.cli("uname -r")

        return {
            "vendor": "MEINBERG",
            "platform": "".join((plat.strip())),
            "version": version,
            "attributes": {
                "codename": codename,
                "distro": distr,
                "kernel": kernel.strip(),
            },
        }
