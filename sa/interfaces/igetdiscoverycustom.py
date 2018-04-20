# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetDiscoveryCustom
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from base import Parameter, DictParameter


class IGetDiscoveryCustom(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetDiscoveryCustom
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from base import *


class IGetDiscoveryCustom(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    instance = Parameter()
    managed_object = Parameter()
    returns = DictParameter()
