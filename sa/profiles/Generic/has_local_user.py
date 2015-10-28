# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.has_local_user
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces import *
import re


class Script(BaseScript):
    name = "Generic.has_local_user"
    interface = IHasLocalUser
    requires = [("get_local_users", IGetLocalUsers)]

    def execute(self, username):
        for u in self.scripts.get_local_users():
            if u["username"] == username:
                return True
        return False
