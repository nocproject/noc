# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Huawei.U2000.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Huawei.U20000.get_version"
    interface = IGetVersion

    def execute(self):
        return None
