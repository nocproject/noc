# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.settings import config


def tt_url(self):
    if self.tt:
        return config.get("tt", "url", 0, {"tt": self.tt})
    else:
        return None
