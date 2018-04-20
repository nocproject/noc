# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_license
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlicense import IGetLicense


class Script(BaseScript):
    name = "Juniper.JUNOS.get_license"
    interface = IGetLicense
=======
##----------------------------------------------------------------------
## Juniper.JUNOS.get_license
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLicense


class Script(NOCScript):
    name = "Juniper.JUNOS.get_license"
    implements = [IGetLicense]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_line = re.compile(
        r"^  (?P<name>\S+)\s+\d+\s+(?P<inst>[1-9]\d*)\s+\d+\s+\S+",
        re.MULTILINE)

    def execute(self):
        r = {}
        for match in self.rx_line.finditer(self.cli("show system license")):
            r[match.group("name")] = int(match.group("inst"))
        return r
