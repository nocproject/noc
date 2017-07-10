# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetChassisID
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.interface.base import BaseInterface
from base import DictListParameter, MACAddressParameter


class IGetChassisID(BaseInterface):
    returns = DictListParameter(attrs={
        "first_chassis_mac": MACAddressParameter(required=False),
        "last_chassis_mac": MACAddressParameter(required=False)
    }, convert=True)
