# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetREPTopology
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import (DictListParameter, MACAddressParameter,
                  StringParameter, IntParameter, BooleanParameter)


class IGetREPTopology(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetREPTopology
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetREPTopology(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Get REP topology information
    """
    returns = DictListParameter(attrs={
        "segment": IntParameter(),
        "topology": DictListParameter(attrs={
            "name": StringParameter(),
            "mac": MACAddressParameter(),
            "port": StringParameter(),
            "edge": StringParameter(required=False, choices=["PRI", "SEC"]),
            "role": StringParameter(required=False, choices=["OPEN", "ALT", "FAIL"]),
            "edge_no_neighbor": BooleanParameter(default=False),
            # Neighbor number (towards open edge)
            "neighbor_number": IntParameter(),
            # Neighbor number (towards alt edge)
            "rev_neighbor_number": IntParameter()
        })
    })
