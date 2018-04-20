# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetDiscoveryID
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from noc.core.interface.base import BaseInterface
from base import (DictParameter,   MACAddressParameter,
                  StringParameter, IPParameter, DictListParameter)


class IGetDiscoveryID(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetDiscoveryID
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from base import (DictParameter, Interface, MACAddressParameter,
                  StringParameter, IPParameter, DictListParameter)


class IGetDiscoveryID(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = DictParameter(attrs={
        # Chassis MAC ranges
        "chassis_mac": DictListParameter(attrs={
            "first_chassis_mac": MACAddressParameter(required=False),
            "last_chassis_mac": MACAddressParameter(required=False)
        }, convert=True, required=False),
        # FQDN
        "hostname": StringParameter(required=False),
        # Router ID/Loopback address
        "router_id": IPParameter(required=False)
    })
