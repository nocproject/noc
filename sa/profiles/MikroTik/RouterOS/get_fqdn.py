# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetFQDN


class Script(NOCScript):
    name = "MikroTik.RouterOS.get_fqdn"
    implements = [IGetFQDN]

    def execute(self):
        s = self.cli("/system identity print")
        return s.split(":", 1)[1].strip()
