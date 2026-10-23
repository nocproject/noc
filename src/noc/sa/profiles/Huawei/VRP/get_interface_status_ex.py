# ---------------------------------------------------------------------
# Huawei.VRP.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_status_ex import Script as BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "Huawei.VRP.get_interface_status_ex"
    interface = IGetInterfaceStatusEx

    def get_iftable(self, oid, ifindexes=None):
        if self.is_cx200X:
            ifindexes = None
        return super().get_iftable(oid, ifindexes)
