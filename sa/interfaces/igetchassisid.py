# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetChassisID
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.interface.base import BaseInterface
from base import DictListParameter, MACAddressParameter


class IGetChassisID(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetChassisID
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from base import Interface, DictListParameter, MACAddressParameter


class IGetChassisID(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = DictListParameter(attrs={
        "first_chassis_mac": MACAddressParameter(required=False),
        "last_chassis_mac": MACAddressParameter(required=False)
    }, convert=True)
