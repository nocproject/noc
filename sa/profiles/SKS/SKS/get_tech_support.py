# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_tech_support
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igettechsupport import IGetTechSupport


class Script(BaseScript):
    name = "SKS.SKS.get_tech_support"
    interface = IGetTechSupport

    def execute(self):
        try:
            c = self.cli("show tech-support")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        return unicode(c, "utf8", "ignore").encode("utf8")
