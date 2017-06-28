# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetLACPNeighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOc modules
from noc.core.interface.base import BaseInterface
from base import (IntParameter, InterfaceNameParameter,
                  MACAddressParameter, DictListParameter)


class IGetLACPNeighbors(BaseInterface):
    returns = DictListParameter(attrs={
        # LAG ID
        "lag_id": IntParameter(),
        # Aggregated interface name
        "interface": InterfaceNameParameter(),
        # Local system id
        "system_id": MACAddressParameter(),
        # List of bundled interfaces
        "bundle": DictListParameter(attrs={
            # Local physical interface name
            "interface": InterfaceNameParameter(),
            # Local LACP port id
            "local_port_id": IntParameter(),
            # remote system id
            "remote_system_id": MACAddressParameter(),
            # remote system's peer port id
            "remote_port_id": IntParameter()
        })
    })
