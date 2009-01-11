import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable
import re

rx_line=re.compile(r"^\*\s+(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+\S+\s+\S+\s+(?P<interfaces>.*)$")

class Script(noc.sa.script.Script):
    name="Cisco.IOS.get_mac_address_table"
    implements=[IGetMACAddressTable]
    def execute(self):
        self.cli("terminal length 0")
        vlans=self.cli("show mac-address-table")
        r=[]
        for l in vlans.split("\n"):
            match=rx_line.match(l.strip())
            if match:
                r.append({
                    "vlan_id"   : match.group("vlan_id"),
                    "mac"       : match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type"      : {"dynamic":"D","static":"S"}[match.group("type")],
                })
        return r
