# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OneAccess.TDRE.get_capabilities_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "OneAccess.TDRE.get_capabilities"

    def execute_platform(self, caps):
        np = len(self.scripts.get_sla_probes())
        caps["OneAccess | IP | SLA | Probes"] = np
