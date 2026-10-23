# ---------------------------------------------------------------------
# ElectronR.KO01M.login
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.ilogin import ILogin


class Script(BaseScript):
    """
    Try to log in
    """

    name = "ElectronR.KO01M.login"
    interface = ILogin
    requires = []

    def execute(self):
        return {"result": True, "message": ""}
