from base import *

class IGetMACAddressTable(Interface):
    returns=ListOfParameter(element=DictParameter(attrs={"vlan_id"    : VLANIDParameter(),
                                                         "mac"        : MACAddressParameter(),
                                                         "interfaces" : StringListParameter(),
                                                         "type"       : StringParameter(), # choices=["D","S"]
                                                         }))
    