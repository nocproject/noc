# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_tech_support
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igettechsupport import IGetTechSupport


class Script(BaseScript):
    name = "Juniper.JUNOS.get_tech_support"
    interface = IGetTechSupport

    def execute(self):
        c = self.cli("request support information")
        return unicode(c, "utf8", "ignore").encode("utf8")
