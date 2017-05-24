# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.login
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.ilogin import ILogin


class Script(BaseScript):
    """
    Try to log in
    """
    name = "Generic.login"
    interface = ILogin
    requires = []

    def execute(self):
        try:
            self.cli("")
            return True
        except:
            return False
