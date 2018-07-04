# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Meinberg.LANTIME.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Meinberg.LANTIME.get_capabilities"
    cache = True

