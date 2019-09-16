# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTP.get_license
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlicense import IGetLicense
from noc.core.validators import is_int


class Script(BaseScript):
    name = "Eltex.LTP.get_license"
    interface = IGetLicense

    rx_line = re.compile(r"^\s+(?P<name>.+\S):\s+(?P<inst>\S+)", re.MULTILINE)

    def execute(self):
        r = {}
        for match in self.rx_line.finditer(self.cli("show license")):
            inst = match.group("inst")
            r[match.group("name")] = int(inst) if is_int(inst) else inst
        return r
