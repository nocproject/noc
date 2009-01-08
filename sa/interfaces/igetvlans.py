from base import *

class IGetVlans(Interface):
    returns=ListOfParameter(element=DictParameter(attrs={"vlan_id":VLANIDParameter(),
                                                         "name":StringParameter(required=False)
                                                         }))
