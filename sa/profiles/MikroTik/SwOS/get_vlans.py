# ---------------------------------------------------------------------
# MikroTik.SwOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "MikroTik.SwOS.get_vlans"
    interface = IGetVlans

    def execute(self):
        vlans = self.profile.parseBrokenJson(self.http.get("/vlan.b", cached=True, eof_mark=b"}"))
        return [{"vlan_id": int(vlan["vid"], 16)} for vlan in vlans]
