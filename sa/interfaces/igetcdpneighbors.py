# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetCDPNeighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import (DictParameter, ListOfParameter, StringParameter,
                  InterfaceNameParameter, IPParameter)


class IGetCDPNeighbors(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetCDPNeighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IGetCDPNeighbors(Interface):
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
<<<<<<< HEAD
            "remote_interface": StringParameter(),
            # Remote IP
            "remote_ip": IPParameter(required=False)
=======
            "remote_interface": StringParameter()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        }))
    })
