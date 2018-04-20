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

rx_ver = re.compile(
    r"ProductCode (?P<version>\S+) build.*Hardware type: (?P<platform>\S+)",
    re.MULTILINE | re.DOTALL)

<<<<<<< HEAD

class Script(BaseScript):
    name = "Protei.MediaGateway.get_version"
    cache = True
    interface = IGetVersion

=======

class Script(noc.sa.script.Script):
    name = "Protei.MediaGateway.get_version"
    cache = True
    implements = [IGetVersion]

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute(self):
        v = self.cli("_version full")
        match = rx_ver.search(v)
        return {
            "vendor": "Protei",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
