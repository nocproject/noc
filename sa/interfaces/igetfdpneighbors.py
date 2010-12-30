# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetFDPNeighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

##
## FDP neighbor information
##
class IGetFDPNeighbors(Interface):
    returns=ListOfParameter(element=DictParameter(attrs={
        "local_interface"    : InterfaceNameParameter(),
        "local_interface_id" : IntParameter(required=False),   # Should be set to locally assigned port identifier
                                                               # When platform advertises ports as local(7) port subtypes
        "neighbors"       : ListOfParameter(element=DictParameter(attrs={
            "remote_device_id"          : StringParameter(),
            "hold_tm"                   : IntParameter(),
            "remote_capability"         : StringParameter(),
            "remote_platform"           : StringParameter(),
            "remote_port_id"            : StringParameter(),
        }))
    }))
