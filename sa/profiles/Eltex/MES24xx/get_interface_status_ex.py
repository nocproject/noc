# ---------------------------------------------------------------------
# Eltex.MES24xx.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interface_status_ex import Script as BaseScript


class Script(BaseScript):
    name = "Eltex.MES24xx.get_interface_status_ex"

    def is_high_speed(self, data, speed) -> bool:
        """
        Detect should we check ifHighSpeed
        :param data: dict with
        :param speed:
        :return:
        """

        if re.search("Te", data["interface"]):
            return True
        else:
            return False
