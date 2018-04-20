# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetBFDSessions
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import (DictListParameter, IPParameter,
                   InterfaceNameParameter, StringParameter, IntParameter, ListOfParameter)


class IGetBFDSessions(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetBFDSessions
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from base import *


class IGetBFDSessions(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = DictListParameter(attrs={
        "local_address": IPParameter(required=False),
        "remote_address": IPParameter(),
        "local_interface": InterfaceNameParameter(),
        "local_discriminator": IntParameter(),
        "remote_discriminator": IntParameter(),
<<<<<<< HEAD
        "state": StringParameter(choices=["UP", "DOWN"]),
        "clients": ListOfParameter(element=StringParameter(choices=[
            "L2", "RSVP", "ISIS", "OSPF", "BGP", "EIGRP", "PIM", "IFNET"
=======
        "state": StringParameter(choices=["UP"]),
        "clients": ListOfParameter(element=StringParameter(choices=[
            "L2", "RSVP", "ISIS", "OSPF", "BGP", "EIGRP", "PIM"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        ])),
        # Transmit interval, microseconds
        "tx_interval": IntParameter(),
        "multiplier": IntParameter(),
        # Detection time, microseconds
        "detect_time": IntParameter()
    })
