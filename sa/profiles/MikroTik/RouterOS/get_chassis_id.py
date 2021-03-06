# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute_cli(self):
        macs = []
        macs += [
            d["mac-address"]
            for n, f, d in self.cli_detail(
                "/interface ethernet print detail without-paging", cached=True
            )
        ]
        macs.sort()
        return [
            {"first_chassis_mac": f, "last_chassis_mac": t} for f, t in self.macs_to_ranges(macs)
        ]
