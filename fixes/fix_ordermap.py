# ----------------------------------------------------------------------
# Upload main_ordermap
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.main.models.ordermap import OrderMap


def fix():
    OrderMap.update_models()
