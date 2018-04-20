# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Cisco.IOS.get_dot11_associations
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdot11associations import IGetDot11Associations


class Script(BaseScript):
    name = "Cisco.IOS.get_dot11_associations"
    interface = IGetDot11Associations
    rx_assoc_line = re.compile(r"^(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}) (?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*$", re.MULTILINE)

=======
##----------------------------------------------------------------------
## Cisco.IOS.get_dot11_associations
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetDot11Associations


class Script(NOCScript):
    name = "Cisco.IOS.get_dot11_associations"
    implements = [IGetDot11Associations]
    rx_assoc_line = re.compile(r"^(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}) (?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*$", re.MULTILINE)

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute(self):
        try:
            assoc = self.cli("show dot11 associations")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        for match in self.rx_assoc_line.findall(assoc):
            r += [{"mac":match.group("mac"), "ip":match.group("ip")}]
        return r
