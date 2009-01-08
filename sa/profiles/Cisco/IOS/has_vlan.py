import noc.sa.script
from noc.sa.interfaces import IHasVlan
import re

class Script(noc.sa.script.Script):
    name="Cisco.IOS.has_vlan"
    implements=[IHasVlan]
    def execute(self,vlan_id):
        for v in self.scripts.get_vlans():
            if v["vlan_id"]==vlan_id:
                return True
        return False
