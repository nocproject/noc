# ---------------------------------------------------------------------
# MikroTik.SwOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import codecs

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "MikroTik.SwOS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        sys_info = self.profile.parseBrokenJson(self.http.get("/sys.b", cached=True, eof_mark=b"}"))
        return {
            "vendor": "MikroTik",
            "platform": codecs.decode(sys_info["brd"], "hex").decode(),
            "version": codecs.decode(sys_info["ver"], "hex").decode(),
            "attributes": {"Serial Number": codecs.decode(sys_info["sid"], "hex").decode()},
        }
