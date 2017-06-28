# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rebuild SelectorCache
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.models.selectorcache import refresh


def fix():
    refresh()
