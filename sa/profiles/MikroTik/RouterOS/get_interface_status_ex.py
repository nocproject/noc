# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS..get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.mib import mib


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
        return data["oper_status"] and speed == self.HIGH_SPEED
