# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_status_ex import Script as BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "DLink.DxS.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    HIGH_SPEED = 0

    def is_high_speed(self, data, speed):
        """
        Detect should we check ifHighSpeed
        :param data: dict with
        :param speed:
        :return:
        """
        # Some devices reporting 1410065408 instead 4294967295
        return speed in [1410065408, 4294967295] and data["oper_status"]
