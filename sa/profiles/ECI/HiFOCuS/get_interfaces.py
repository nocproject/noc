# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ECI.HiFOCuS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# -------------------------------------------------------------------

# Python modules
from __future__ import print_function

# import re
import six

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces

# from noc.core.ip import IPv4


class Script(BaseScript):
    name = "ECI.HiFOCuS.get_interfaces"
    interface = IGetInterfaces
    reuse_cli_session = False
    keep_cli_session = False

    def execute_cli(self, **kwargs):
        boards = self.profile.get_boards(self)
        shelf_num = 0
        interfaces = {}
        for board in boards:
            if board["card_type"].startswith("ATUC"):
                # xDSL cards
                v = self.cli("GXTURPOP %d %d" % (shelf_num, board["slot"]))
                for row in self.profile.parse_table(v):
                    ifindex, port = row[:2]
                    port = "%d/%d/%d" % (shelf_num, board["slot"], int(port))
                    interfaces[port] = {
                        "name": port,
                        "type": "physical",
                        "admin_status": True,
                        "oper_status": True,
                        "ifindex": ifindex,
                        "subinterfaces": [],  # "enabled_afi": ["ATM"],
                    }
        return [{"interfaces": sorted(six.itervalues(interfaces), key=lambda x: x["name"])}]
