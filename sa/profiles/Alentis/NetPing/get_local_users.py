# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alentis.NetPing.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetLocalUsers


class Script(BaseScript):
    name = "Alentis.NetPing.get_local_users"
    interface = IGetLocalUsers

    def execute(self):
        data = self.profile.var_data(self, "/setup_get.cgi")
        r = [{
            "username": data["uname"],
            "class": "superuser",
            "is_active": True
            }]
        return r
