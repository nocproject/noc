# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetVRF
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetVRF(Interface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "name": StringParameter(),
        "rd": RDParameter(),
        "interfaces": ListOfParameter(element=InterfaceNameParameter())
    }))
