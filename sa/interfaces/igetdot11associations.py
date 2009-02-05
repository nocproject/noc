from base import *

class IGetDot11Associations(Interface):
    returns=ListOfParameter(element=DictParameter(attrs={
        "mac" : MACAddressParameter(),
        "ip"  : IPParameter(required=False),
    }))
