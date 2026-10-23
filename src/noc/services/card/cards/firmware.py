# ---------------------------------------------------------------------
# Firmware card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.inv.models.firmware import Firmware
from .base import BaseCard


class FirmwarePlanCard(BaseCard):
    name = "firmware"
    default_template_name = "firmware"
    model = Firmware

    def get_data(self):
        return {"object": self.object}
