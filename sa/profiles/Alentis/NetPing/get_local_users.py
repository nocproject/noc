# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alentis.NetPing.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLocalUsers


class Script(NOCScript):
    name = "Alentis.NetPing.get_local_users"
    implements = [IGetLocalUsers]

    def execute(self):
        data = self.profile.var_data(self, "/setup_get.cgi")
        r = [{
            "username": data["uname"],
            "class": "superuser",
            "is_active": True
            }]
        return r
