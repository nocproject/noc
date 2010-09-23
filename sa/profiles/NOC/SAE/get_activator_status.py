# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC.SAE.get_activator_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetObjectStatus

class Script(noc.sa.script.Script):
    name="NOC.SAE.get_activator_status"
    implements=[IGetObjectStatus]
    def execute(self):
        from noc.sa.models import Activator
        r=[]
        for a in Activator.objects.filter(is_active=True):
            try:
                self.sae.factory.get_socket_by_name(a.name)
                status=True
            except:
                status=False
            r+=[{
                "name"   : a.name,
                "status" : status
            }]
        return r
