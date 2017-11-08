# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Upload main_ordermap
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
# NOC modules
from noc.main.models.ordermap import OrderMap


def fix():
    OrderMap.update_models()
