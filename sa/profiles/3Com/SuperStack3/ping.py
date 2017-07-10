# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3.ping
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "3Com.SuperStack3.ping"
    interface = IPing

    def execute(self, address):
        v = self.cli("protocol ip ping %s" % address)
        if "No answer from" in v:
            return {"success": 0, "count": 1}
        else:
            return {"success": 1, "count": 1}
