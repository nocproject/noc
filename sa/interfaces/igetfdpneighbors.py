# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetFDPNeighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import DictParameter, ListOfParameter, StringParameter, InterfaceNameParameter


class IGetFDPNeighbors(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetFDPNeighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IGetFDPNeighbors(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = DictParameter(attrs={
        # Local device id: FQDN or serial number
        "device_id": StringParameter(),
        "neighbors": ListOfParameter(element=DictParameter(attrs={
            # Remote device id: FQDN or serial number
            "device_id": StringParameter(),
            # Local interface
            "local_interface": InterfaceNameParameter(),
            # Remote interface
            "remote_interface": StringParameter()
        }))
    })
