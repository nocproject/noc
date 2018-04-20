# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, DictParameter,
                  StringParameter, VLANIDParameter)


<<<<<<< HEAD
class IGetVlans(BaseInterface):
=======
class IGetVlans(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = ListOfParameter(element=DictParameter(attrs={
        "vlan_id": VLANIDParameter(),
        "name": StringParameter(required=False)
    }))
    preview = "NOC.sa.managedobject.scripts.ShowVLANs"
