# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_tech_support
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igettechsupport import IGetTechSupport
from noc.core.comp import smart_text, smart_bytes


class Script(BaseScript):
    name = "Juniper.JUNOS.get_tech_support"
    interface = IGetTechSupport

    def execute(self):
        c = self.cli("request support information")
        return smart_bytes(smart_text(c, errors="ignore"))
