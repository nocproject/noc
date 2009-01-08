from base import *

class IHasVlan(Interface):
    vlan_id=VLANIDParameter()
    returns=BooleanParameter()