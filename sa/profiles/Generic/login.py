# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.login
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.core.error import NOCError
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
            return {"result": True, "message": ""}
        except NOCError as e:
            return {"result": False, "message": "Error: %s (%s)" % (e.default_msg, e.message)}
        except Exception as e:
            return {"result": False, "message": "Exception: %s" % repr(e)}
