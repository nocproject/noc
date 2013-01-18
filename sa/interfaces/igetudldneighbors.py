# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetUDLDNeighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from base import *


class IGetUDLDNeighbors(Interface):
    returns = DictListParameter(attrs={
        "local_device": StringParameter(),
        "local_interface": InterfaceNameParameter(),
        "remote_device": StringParameter(),
        "remote_interface": StringParameter(),
        "state": StringParameter(choices=["BIDIRECTIONAL"])
    })
