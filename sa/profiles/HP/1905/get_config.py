# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.1905.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "HP.1905.get_config"
    interface = IGetConfig

    def execute(self, TFTP_root="", TFTP_IP="", file_name="", **kwargs):
        # Try snmp first
        #
        #
        # See bug NOC-291: http://bt.nocproject.org/browse/NOC-291
        raise self.NotSupportedError("Not supported on")
