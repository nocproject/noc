# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_license
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlicense import IGetLicense


class Script(BaseScript):
    name = "Juniper.JUNOS.get_license"
    interface = IGetLicense

    rx_line = re.compile(
        r"^  (?P<name>\S+)\s+\d+\s+(?P<inst>[1-9]\d*)\s+\d+\s+\S+",
        re.MULTILINE)

    def execute(self):
        r = {}
        for match in self.rx_line.finditer(self.cli("show system license")):
            r[match.group("name")] = int(match.group("inst"))
        return r
