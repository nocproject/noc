# ---------------------------------------------------------------------
# IGetLLDPNeighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import (
    DictListParameter,
    StringParameter,
    IntParameter,
    InterfaceNameParameter,
    MACAddressParameter,
    IPv4Parameter,
)


#
# LLDP neighbor information
#
# Rules:
# local_inteface must be filled with interface name (will be cleaned automatically)
#
# local_interface_id depens upon how the box advertises own interfaces:
#
# If interfaces advertised with macAddress(3) LldpPortIdSubtype,
# local_interface_id must be set to interface MAC address
# (will be cleaned automatically)
#
# If interface advertised with networkAddress(4) LldpPortIdSubtype,
# local_interface_id must be set to interface IP address
#
# If interfaces advertised with interfaceName(5) LldpPortIdSubtype,
# local_interface_id must be left empty or ommited.
#
# If interfaces advertised with local(7) LldpPortIdSubtype,
# local_interface_id must be set to local identifier
#
# Remote port handling solely depends upon remote_port_subtype:
#
# For macAddress(3) - convert to common normalized form
#
# For networkAddress(4) - return as IP address
#
# For interfaceName(5) - return untouched
#
# For local(7) - convert to integer and return untouched
#
class IGetLLDPNeighbors(BaseInterface):
    returns = DictListParameter(
        attrs={
            "local_interface": InterfaceNameParameter(),
            # Should be set when platform advertises not LldpPortIdSubtype==5
            "local_interface_id": IntParameter(required=False)
            | MACAddressParameter(required=False)
            | IPv4Parameter(required=False),
            "neighbors": DictListParameter(
                attrs={
                    # LldpChassisIdSubtype TC, macAddress(4)
                    "remote_chassis_id_subtype": IntParameter(default=4),
                    # Remote chassis ID
                    "remote_chassis_id": MACAddressParameter(accept_bin=False)
                    | IPv4Parameter()
                    | StringParameter(),
                    # LldpPortIdSubtype TC, interfaceName(5)
                    "remote_port_subtype": IntParameter(default=5),
                    "remote_port": MACAddressParameter(accept_bin=False)
                    | IPv4Parameter()
                    | StringParameter(),
                    "remote_port_description": StringParameter(required=False),
                    "remote_system_name": StringParameter(required=False),
                    "remote_system_description": StringParameter(required=False),
                    "remote_mgmt_address": IPv4Parameter(required=False),
                    # LldpSystemCapabilitiesMap TC bitmask
                    "remote_capabilities": IntParameter(default=0),
                }
            ),
        }
    )
