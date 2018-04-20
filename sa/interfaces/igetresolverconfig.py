# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetResolverConfig interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import (DictParameter, ListOfParameter,
                  IPParameter, StringParameter, StringListParameter)


class IGetResolverConfig(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetResolverConfig interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetResolverConfig(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = DictParameter(attrs={
        "domain": StringParameter(required=False),
        "search": StringListParameter(required=False),
        "nameservers": ListOfParameter(element=IPParameter(), required=False)
    })
