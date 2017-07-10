# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_dot11_associations
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdot11associations import IGetDot11Associations


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_dot11_associations"
    interface = IGetDot11Associations

    def execute(self, interface=None):
        cmd = "/interface wireless registration-table print stats without-paging"
        if interface is not None:
            cmd += " where interface=%s" % interface
        try:
            v = self.cli_detail(cmd)
        except self.CLISyntaxError:
            return []
        return [{
            "mac": r["mac-address"],
            "ip": r["last-ip"].split()[0]
        } for n, f, r in v]
