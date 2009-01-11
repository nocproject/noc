from base import *

class IGetVersion(Interface):
    returns=DictParameter(attrs={
                                "vendor"  : StringParameter(),
                                "platform": StringParameter(),
                                "version" : StringParameter(),
                                "image"   : StringParameter(required=False)
                                })