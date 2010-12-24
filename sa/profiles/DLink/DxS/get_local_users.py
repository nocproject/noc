# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetLocalUsers
import re,datetime

rx_line=re.compile(r"^(?P<username>\S+)\s+(?P<privilege>Admin|Operator|User)$")

class Script(noc.sa.script.Script):
    name="DLink.DxS.get_local_users"
    implements=[IGetLocalUsers]
    def execute(self):
        data=self.cli("show account")
        r=[]
        for l in data.split("\n"):
            match=rx_line.match(l.strip())
            if match:
                r.append({
                    "username" : match.group("username"),
                    "class"    : {"Admin":"superuser","Operator":"operator","User":"operator"}[match.group("privilege")],
                    "is_active": True
                    })
        return r
