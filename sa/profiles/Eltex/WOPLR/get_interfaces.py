# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.WOPLR.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Eltex.WOPLR.get_interfaces"
    interface = IGetInterfaces
