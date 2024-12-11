# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_status_ex import Script as BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    HIGH_SPEED = 0

    def is_high_speed(self, data, speed):
        """
        Detect should we check ifHighSpeed
        :param data: dict with
        :param speed:
        :return:
        """
        return data.get("oper_status") and speed == self.HIGH_SPEED
