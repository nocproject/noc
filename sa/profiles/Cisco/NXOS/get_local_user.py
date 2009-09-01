# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.NXOS.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetLocalUsers

class Script(noc.sa.script.Script):
    name="Cisco.NXOS.get_local_users"
    implements=[IGetLocalUsers]
    def execute(self):
        data=self.cli("show user-account | no-more")
        r=[]
        cu={}
        for l in data.split("\n"):
            l=l.strip()
            if l.startswith("user:"):
                if cu:
                    r+=[cu]
                cu={"username":l[5:],"is_active":True}
            elif cu and l.startswith("roles:"):
                for role in l[6:].split(" "):
                    if role=="network-operator":
                        role="operator"
                    elif role=="network-admin":
                        role="superuser"
                    if "class" not in cu:
                        cu["class"]=role
                    else:
                        if cu["class"]=="superuser":
                            continue
                        else:
                            cu["class"]=role
        if cu:
            r+=[cu]
        return r
