# -*- coding: utf-8 -*-
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
    returns = DictParameter(attrs={
        # Local device id: FQDN or serial number
        "device_id": StringParameter(),
        "neighbors": ListOfParameter(element=DictParameter(attrs={
            # Remote device id: FQDN or serial number
            "device_id": StringParameter(),
            # Local interface
            "local_interface": InterfaceNameParameter(),
            # Remote interface
            "remote_interface": StringParameter(),
            # Remote IP
            "remote_ip": IPParameter(required=False)
        }))
    })
