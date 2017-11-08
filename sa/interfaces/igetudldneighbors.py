# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetUDLDNeighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface

from base import DictListParameter, InterfaceNameParameter, StringParameter


class IGetUDLDNeighbors(BaseInterface):
    returns = DictListParameter(attrs={
        "local_device": StringParameter(),
        "local_interface": InterfaceNameParameter(),
        "remote_device": StringParameter(),
        "remote_interface": StringParameter(),
        "state": StringParameter(choices=["BIDIRECTIONAL"])
    })
