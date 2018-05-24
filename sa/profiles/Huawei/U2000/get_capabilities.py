# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Huawei.U2000.get_capabilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "Huawei.U2000.get_capabilities"
    cache = True

    def execute_platform_cli(self, caps):
        caps["Mobile | BSC"] = True
