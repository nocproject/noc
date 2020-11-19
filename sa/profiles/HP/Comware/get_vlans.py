# ---------------------------------------------------------------------
# HP.Comware.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_vlans import Script as BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "HP.Comware.get_vlans"
    interface = IGetVlans

    def execute_cli(self, **kwargs):
        vlans = self.strip_first_lines(self.cli("display vlan"), 2)
        vlans = vlans.replace("The following VLANs exist:\n", "")
        vlans = vlans.replace("(default)", "")
        vlans = vlans.replace("(reserved)", "")
        vlans = vlans.replace("\n", ",")
        vlans = self.expand_rangelist(vlans)
        r = []
        for v in vlans:
            if int(v) == 1:
                continue
            r += [{"vlan_id": int(v)}]
        return r
