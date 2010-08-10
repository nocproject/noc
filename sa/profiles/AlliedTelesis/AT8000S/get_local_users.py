# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.get_local_users
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

rx_line=re.compile(r"^(?P<username>\S+)\s+(?P<privilege>1|15)$")

class Script(noc.sa.script.Script):
    name="AlliedTelesis.AT8000S.get_local_users"
    implements=[IGetLocalUsers]
    def execute(self):
        data=self.cli("show users accounts")
        r=[]
        for l in data.split("\n"):
            match=rx_line.match(l.strip())
            if match:
                r.append({
                    "username" : match.group("username"),
                    "class"    : {"15":"superuser","1":"operator"}[match.group("privilege")],
                    "is_active": True
                    })
        return r