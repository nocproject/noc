# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DVG.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_arp import Script as BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "DLink.DVG.get_arp"
    interface = IGetARP
    cache = True
