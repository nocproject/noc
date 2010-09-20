# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetLLDPNeighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

##
## LLDP neighbor information
##
class IGetLLDPNeighbors(Interface):
    returns=ListOfParameter(element=DictParameter(attrs={
        "local_interface"    : InterfaceNameParameter(),
        "local_interface_id" : IntParameter(required=False)|MACAddressParameter(required=False)|IPParameter(required=False), # Should be set when platform advertises not LldpPortIdSubtype==5
        "neighbors"       : ListOfParameter(element=DictParameter(attrs={
            "remote_chassis_id_subtype" : IntParameter(default=4), # LldpChassisIdSubtype TC, macAddress(4)
            "remote_chassis_id"         : MACAddressParameter() | IPParameter() , # Remote chassis ID
            "remote_port_subtype"       : IntParameter(default=5), # LldpPortIdSubtype TC, interfaceName(5)
            "remote_port"               : StringParameter(),
            "remote_system_name"        : StringParameter(required=False),
            "remote_capabilities"       : IntParameter(default=0), # LldpSystemCapabilitiesMap TC bitmask
        }))
    }))
