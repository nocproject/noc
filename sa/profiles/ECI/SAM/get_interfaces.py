# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ECI.SAM.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.lib.text import list_to_ranges

import re


class Script(BaseScript):
    name = "ECI.SAM.get_interfaces"
    interface = IGetInterfaces

    def execute(self):
        interfaces = []
        interfaces += [{
                "name": 1,
                "type": "physical",
                "admin_status": True,
                "oper_status": True,
                "subinterfaces": [{
                    "name": 1,
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": ["BRIDGE"],
                }]
            }]
        return [{"interfaces": interfaces}]
