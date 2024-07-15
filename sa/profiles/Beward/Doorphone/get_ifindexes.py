# ---------------------------------------------------------------------
# Beward.Doorphone.get_ifindexes
# ---------------------------------------------------------------------
# Copyright (C) 2023-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_status_ex import Script as BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "Beward.Doorphone.get_ifindexes"
    interface = IGetInterfaceStatusEx
