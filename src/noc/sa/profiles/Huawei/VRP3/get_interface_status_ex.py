# ---------------------------------------------------------------------
# Huawei.VRP3.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_status_ex import Script as BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "Huawei.VRP3.get_interface_status_ex"
    interface = IGetInterfaceStatusEx

    MAX_REPETITIONS = 10

    def execute_snmp(self, interfaces=None, **kwargs):
        r = self.get_data(interfaces=interfaces, raw_speed_value=True)
        for x in r:
            # ADSL port return value as kb/sec
            # For SNMP Timeout we getting interfaces only list
            if x["interface"].startswith("FE") and "out_speed" in x:
                x["out_speed"] = x["out_speed"] // 1000
            if x["interface"].startswith("FE") and "in_speed" in x:
                x["in_speed"] = x["in_speed"] // 1000
        return r
