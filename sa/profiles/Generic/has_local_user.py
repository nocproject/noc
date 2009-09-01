# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.has_local_user
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import *
import re

class Script(noc.sa.script.Script):
    name="Generic.has_local_user"
    implements=[IHasLocalUser]
    requires=[("get_local_users",IGetLocalUsers)]
    def execute(self,username):
        for u in self.scripts.get_local_users():
            if u["username"]==username:
                return True
        return False
