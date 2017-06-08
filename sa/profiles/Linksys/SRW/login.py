# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linksys.SWR.login
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
    name = "Linksys.SWR.login"
    interface = ILogin
    requires = []

    def execute(self):
        try:
            self.cli("\x1A")
            return True
        except:
            return False
