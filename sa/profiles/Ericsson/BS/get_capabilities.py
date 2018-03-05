# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Ericsson.BS.get_capabilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "Ericsson.BC.get_capabilities"
    cache = True

    def execute_platform(self, caps):
        caps["Mobile | BS"] = True
