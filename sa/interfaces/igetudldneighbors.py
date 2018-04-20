# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetUDLDNeighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from base import DictListParameter, InterfaceNameParameter, StringParameter


class IGetUDLDNeighbors(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetUDLDNeighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from base import *


class IGetUDLDNeighbors(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = DictListParameter(attrs={
        "local_device": StringParameter(),
        "local_interface": InterfaceNameParameter(),
        "remote_device": StringParameter(),
        "remote_interface": StringParameter(),
        "state": StringParameter(choices=["BIDIRECTIONAL"])
    })
