# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_capabilities_ex
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modiles
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetcapabilitiesex import IGetCapabilitiesEx


class Script(NOCScript):
    name = "MikroTik.RouterOS.get_capabilities_ex"
    cache = True
    implements = [IGetCapabilitiesEx]
    rx_lic = re.compile(
        r"^\s*software-id: (?P<sid>\S+).+upgradable-to: (?P<upto>\S+).+nlevel:"
        r" (?P<nlevel>\d+).+features:.*(?P<features>\.*)$",
        re.MULTILINE | re.DOTALL)

    def check_license(self, caps):
        v = self.cli("/system license print")
        match = self.re_search(self.rx_lic, v)
        caps["MikroTik | RouterOS | Software Id"] = match.group("sid")
        caps["MikroTik | RouterOS | Level"] = int(match.group("nlevel"))
        caps["MikroTik | RouterOS | Upgradable To"] = match.group("upto")

    def execute(self, caps={}):
        self.check_license(caps)
        return caps
