# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DVG.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "DLink.DVG.get_interfaces"
    cache = True
    interface = IGetInterfaces
