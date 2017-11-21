# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ruckus.SmartZone.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Ruckus.SmartZone.get_config"
    interface = IGetConfig
