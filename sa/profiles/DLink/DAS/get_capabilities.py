# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DAS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.core.mib import mib


class Script(BaseScript):
    name = "DLink.DAS.get_capabilities"

    CHECK_SNMP_GETNEXT = {"SNMP | MIB | ADSL-MIB": mib["ADSL-LINE-MIB::adslLineCoding"]}
